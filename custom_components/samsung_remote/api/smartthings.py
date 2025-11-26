"""SmartThings API client for Samsung devices - Simplified Authentication."""

import asyncio
import time
from typing import Any, Optional

import aiohttp

from ..const import (
    DEFAULT_TIMEOUT,
    LOGGER,
    SAMSUNG_KEY_MAP,
    SMARTTHINGS_COMMANDS,
)


class SmartThingsAPI:
    """SmartThings API client with simple Personal Access Token authentication."""

    def __init__(
        self,
        hass,
        token: str,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize SmartThings client with PAT token."""
        self.hass = hass
        self.token = token.strip() if token else None
        self.timeout = timeout
        self.base_url = "https://api.smartthings.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.device_cache: dict[str, dict[str, Any]] = {}
        self.device_capabilities: dict[str, list[str]] = {}
        self._command_lock = asyncio.Lock()
        self._last_command_time = 0.0

        LOGGER.debug("Initialized SmartThings API with PAT token")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make API request with retry logic."""
        if not self.token:
            raise Exception("API token is not set. Please reconfigure the integration.")

        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.token.strip()}",
            "Content-Type": "application/json",
        }

        try:
            async with session.request(
                method,
                url,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status in (200, 201):
                    return await resp.json()
                elif resp.status == 401:
                    error_text = await resp.text()
                    LOGGER.error(f"401 Unauthorized from SmartThings API: {error_text[:200]}")
                    raise Exception(
                        f"SmartThings Authentication failed (401 Unauthorized). "
                        f"Token may be invalid or expired. Please check your token at "
                        f"https://account.smartthings.com/tokens"
                    )
                elif resp.status == 403:
                    error_text = await resp.text()
                    LOGGER.error(f"SmartThings API 403 Forbidden: {error_text[:200]}")
                    raise Exception(
                        f"SmartThings API Permission Error (403 Forbidden). "
                        f"Your token lacks required permissions. "
                        f"Ensure your token has 'r:devices:*' AND 'x:devices:*' scopes. "
                        f"Response: {error_text[:200]}"
                    )
                elif resp.status == 429 and retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    LOGGER.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, endpoint, data, retry_count + 1, max_retries
                    )
                else:
                    error_text = await resp.text()
                    raise Exception(
                        f"SmartThings API error {resp.status}: {error_text[:200]}"
                    )
        except asyncio.TimeoutError:
            if retry_count < max_retries:
                LOGGER.warning("Request timeout, retrying...")
                await asyncio.sleep(2 ** retry_count)
                return await self._request(
                    method, endpoint, data, retry_count + 1, max_retries
                )
            raise
        except Exception as e:
            LOGGER.error(f"Request failed: {e}")
            raise

    async def get_devices(self) -> list[dict[str, Any]]:
        """Fetch all devices from SmartThings."""
        try:
            response = await self._request("GET", "/devices")
            devices = response.get("items", [])
            
            # Cache and filter for TV devices
            tv_devices = []
            for device in devices:
                if self._is_tv_device(device):
                    device_id = device["deviceId"]
                    self.device_cache[device_id] = device
                    
                    # Cache capabilities for this device
                    capabilities = self._get_device_capabilities(device)
                    self.device_capabilities[device_id] = capabilities
                    LOGGER.info(f"Device {device.get('label', device_id)} capabilities: {capabilities}")
                    
                    tv_devices.append(device)
            
            LOGGER.info(f"Found {len(tv_devices)} TV devices")
            return tv_devices
        except Exception as e:
            LOGGER.error(f"Failed to fetch devices: {e}")
            raise

    def _get_device_capabilities(self, device: dict[str, Any]) -> list[str]:
        """Extract capabilities from device."""
        capabilities = []
        components = device.get("components", [])
        if components and isinstance(components, list):
            for component in components:
                caps = component.get("capabilities", [])
                for cap in caps:
                    if isinstance(cap, dict):
                        cap_id = cap.get("id", "")
                        if cap_id:
                            capabilities.append(cap_id)
        return capabilities

    def _is_tv_device(self, device: dict[str, Any]) -> bool:
        """Check if device is a TV."""
        device_type = device.get("deviceTypeName", "").lower()
        device_type_id = device.get("deviceType", "").lower()
        
        # Check device type
        if "tv" in device_type or "tv" in device_type_id:
            return True
        
        # Check capabilities
        capabilities = self._get_device_capabilities(device)
        tv_capabilities = [
            "samsungvd.remoteControl", 
            "samsungvd.mediaInputSource",
            "samsungvd.ambientContent",
            "mediaPlayback", 
            "tvChannel", 
            "audioVolume"
        ]
        
        if any(cap in capabilities for cap in tv_capabilities):
            return True
        
        return False

    async def send_command(self, device_id: str, command: str) -> bool:
        """Send remote command to device using SmartThings API."""
        async with self._command_lock:
            try:
                current_time = time.time()
                time_since_last = current_time - self._last_command_time
                min_delay = 0.3
                
                if time_since_last < min_delay:
                    delay_needed = min_delay - time_since_last
                    LOGGER.debug(f"Throttling: waiting {delay_needed:.2f}s before sending command")
                    await asyncio.sleep(delay_needed)
                
                key = SAMSUNG_KEY_MAP.get(command, command)
                
                if key not in SMARTTHINGS_COMMANDS:
                    LOGGER.warning(
                        f"Command '{command}' (key: {key}) is not supported by SmartThings API. "
                        f"This command only works with Tizen Local API. "
                        f"Supported SmartThings commands: {', '.join(sorted(SMARTTHINGS_COMMANDS))}"
                    )
                    return False
                
                payload = {
                    "commands": [
                        {
                            "component": "main",
                            "capability": "samsungvd.remoteControl",
                            "command": "send",
                            "arguments": [key]
                        }
                    ]
                }
                
                LOGGER.debug(f"Sending command to {device_id}: capability=samsungvd.remoteControl, command=send, key={key}")
                
                await self._request("POST", f"/devices/{device_id}/commands", payload)
                self._last_command_time = time.time()
                LOGGER.debug(f"Successfully sent command {command} (key: {key})")
                return True
                
            except Exception as e:
                error_msg = str(e)
                LOGGER.error(f"Failed to send command {command} (key: {key}): {error_msg}")
                
                if "403" in error_msg:
                    LOGGER.error(
                        f"Permission Denied! Your SmartThings token is missing the 'x:devices:*' (execute) scope. "
                        f"Please generate a new token with ALL required scopes: r:devices:*, x:devices:* "
                        f"See documentation: https://github.com/Qlimuli/samsung-tv-remote-HA/blob/main/docs/SMARTTHINGS_SETUP.md"
                    )
                
                if "422" in error_msg or "ConstraintViolationError" in error_msg:
                    LOGGER.error(
                        f"API rejected command. This might mean:\n"
                        f"1. The key code '{key}' is not supported by SmartThings\n"
                        f"2. The TV is offline\n"
                        f"3. The capability format is wrong\n"
                        f"Supported commands: {', '.join(sorted(SMARTTHINGS_COMMANDS))}"
                    )
                
                return False

    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        """Get device status."""
        try:
            response = await self._request("GET", f"/devices/{device_id}/status")
            return response
        except Exception as e:
            LOGGER.error(f"Failed to get device status: {e}")
            return {}

    async def validate_token(self) -> bool:
        """Validate SmartThings token by attempting to fetch devices."""
        try:
            if not self.token:
                LOGGER.error("Token is not set")
                return False
            
            token_length = len(self.token)
            token_first_20 = self.token[:20]
            token_last_10 = self.token[-10:]
            LOGGER.debug(f"Token validation - Length: {token_length}, First 20: {token_first_20}..., Last 10: ...{token_last_10}")
            
            session = await self._get_session()
            url = f"{self.base_url}/devices"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            LOGGER.info(f"Starting token validation with SmartThings API...")
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    is_valid = "items" in response_data
                    LOGGER.info(f"Token validation: {'success' if is_valid else 'failed'} - Response contains 'items': {is_valid}")
                    return is_valid
                elif resp.status == 401:
                    error_text = await resp.text()
                    LOGGER.error(f"Token validation failed: 401 Unauthorized - Token is invalid or expired. Response: {error_text}")
                    return False
                elif resp.status == 403:
                    error_text = await resp.text()
                    LOGGER.error(f"Token validation failed: 403 Forbidden - Token lacks permissions. Response: {error_text}")
                    return False
                else:
                    error_text = await resp.text()
                    LOGGER.error(f"Token validation failed ({resp.status}): {error_text}")
                    return False

        except aiohttp.ClientConnectorDNSError as e:
            LOGGER.warning(f"Token validation could not complete due to network/DNS error: {e}. Assuming token is valid to allow startup.")
            return True
        except asyncio.TimeoutError:
            LOGGER.warning("Token validation timed out. Assuming network issue and allowing startup.")
            return True
        except Exception as e:
            LOGGER.error(f"Token validation failed with unexpected error: {e}", exc_info=True)
            return False

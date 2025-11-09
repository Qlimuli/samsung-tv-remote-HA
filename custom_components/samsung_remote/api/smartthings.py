"""SmartThings API client for Samsung devices."""

import asyncio
from typing import Any, Optional

import aiohttp
from homeassistant.core import HomeAssistant

from ..const import DEFAULT_TIMEOUT, LOGGER, SAMSUNG_KEY_MAP


class SmartThingsAPI:
    """SmartThings API client."""

    def __init__(self, hass: HomeAssistant, token: str, timeout: int = DEFAULT_TIMEOUT):
        """Initialize SmartThings client."""
        self.hass = hass
        self.token = token
        self.timeout = timeout
        self.base_url = "https://api.smartthings.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.device_cache: dict[str, dict[str, Any]] = {}
        self.device_capabilities: dict[str, list[str]] = {}

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
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
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
                elif resp.status == 429 and retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    LOGGER.warning(f"Rate limited, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    return await self._request(
                        method, endpoint, data, retry_count + 1, max_retries
                    )
                else:
                    error_text = await resp.text()
                    raise Exception(f"SmartThings API error {resp.status}: {error_text}")
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
        """Send remote command to device using SmartThings API.
        
        For Samsung TVs, we need to use the samsungvd.remoteControl capability
        with the 'send' command and the key code as argument.
        """
        try:
            key = SAMSUNG_KEY_MAP.get(command, command)
            
            # Samsung TVs use samsungvd.remoteControl capability
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
            LOGGER.debug(f"Successfully sent command {command} (key: {key})")
            return True
            
        except Exception as e:
            error_msg = str(e)
            LOGGER.error(f"Failed to send command {command} (key: {key}): {error_msg}")
            
            # Log more details on first failure to help debug
            if "422" in error_msg or "ConstraintViolationError" in error_msg:
                LOGGER.error(
                    f"API rejected command. This might mean:\n"
                    f"1. The key code '{key}' is not supported\n"
                    f"2. The TV is offline\n"
                    f"3. The capability format is wrong"
                )
                
                # Try to get available commands from the capability
                try:
                    cap_details = await self._request(
                        "GET", 
                        f"/capabilities/samsungvd.remoteControl/1"
                    )
                    LOGGER.debug(f"Capability details: {cap_details}")
                except Exception:
                    pass
            
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
        """Validate SmartThings token."""
        try:
            response = await self._request("GET", "/devices")
            is_valid = "items" in response
            LOGGER.debug(f"Token validation: {'success' if is_valid else 'failed'}")
            return is_valid
        except Exception as e:
            LOGGER.error(f"Token validation failed: {e}")
            return False

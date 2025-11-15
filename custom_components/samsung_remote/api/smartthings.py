"""SmartThings API client for Samsung devices."""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import aiohttp
from homeassistant.core import HomeAssistant

from ..const import (
    DEFAULT_TIMEOUT,
    LOGGER,
    SAMSUNG_KEY_MAP,
    SMARTTHINGS_COMMANDS,
    SMARTTHINGS_OAUTH_TOKEN_URL,
    CONF_SMARTTHINGS_ACCESS_TOKEN,
    CONF_SMARTTHINGS_REFRESH_TOKEN,
    CONF_SMARTTHINGS_TOKEN_EXPIRES,
)


class SmartThingsAPI:
    """SmartThings API client with OAuth 2.0 token refresh support."""

    def __init__(
        self,
        hass: HomeAssistant,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires: Optional[float] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize SmartThings client."""
        self.hass = hass
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires = token_expires
        self.timeout = timeout
        self.base_url = "https://api.smartthings.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.device_cache: dict[str, dict[str, Any]] = {}
        self.device_capabilities: dict[str, list[str]] = {}
        self._command_lock = asyncio.Lock()
        self._last_command_time = 0.0

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

    async def _refresh_token_if_needed(self) -> bool:
        """Refresh OAuth token if it's about to expire."""
        if not self.refresh_token:
            LOGGER.error("No refresh token available for token refresh")
            return False

        # Check if token is expired or about to expire (within 5 minutes)
        if self.token_expires:
            time_until_expiry = self.token_expires - time.time()
            if time_until_expiry > 300:  # 5 minutes buffer
                return True

        try:
            LOGGER.debug("Refreshing SmartThings OAuth token...")
            session = await self._get_session()

            # Exchange refresh token for new access token
            async with session.post(
                SMARTTHINGS_OAUTH_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": "homeassistant-samsung-remote",  # Home Assistant's public client
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    self.access_token = response_data["access_token"]
                    # Refresh token might be rotated
                    if "refresh_token" in response_data:
                        self.refresh_token = response_data["refresh_token"]
                    # Update token expiry (expires_in is in seconds)
                    expires_in = response_data.get("expires_in", 86400)
                    self.token_expires = time.time() + expires_in

                    LOGGER.debug("SmartThings OAuth token refreshed successfully")

                    # Store updated tokens in config entry
                    if self.hass.data.get("samsung_remote"):
                        for entry in self.hass.config_entries.async_entries(
                            "samsung_remote"
                        ):
                            new_data = {**entry.data}
                            new_data[CONF_SMARTTHINGS_ACCESS_TOKEN] = (
                                self.access_token
                            )
                            new_data[CONF_SMARTTHINGS_REFRESH_TOKEN] = (
                                self.refresh_token
                            )
                            new_data[CONF_SMARTTHINGS_TOKEN_EXPIRES] = (
                                self.token_expires
                            )
                            self.hass.config_entries.async_update_entry(
                                entry, data=new_data
                            )

                    return True
                else:
                    error_text = await resp.text()
                    LOGGER.error(
                        f"Failed to refresh token: {resp.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            LOGGER.error(f"Error refreshing token: {e}")
            return False

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make API request with retry logic and automatic token refresh."""
        if not await self._refresh_token_if_needed():
            if self.refresh_token:  # Only fail if we have a refresh token but it failed
                raise Exception("Failed to refresh OAuth token")

        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
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
                    # Token might be invalid, try to refresh and retry once
                    if retry_count == 0 and self.refresh_token:
                        LOGGER.warning("Got 401, attempting token refresh...")
                        if await self._refresh_token_if_needed():
                            return await self._request(
                                method, endpoint, data, retry_count + 1, max_retries
                            )

                    error_text = await resp.text()
                    LOGGER.error(
                        f"SmartThings Authentication failed (401): {error_text}"
                    )
                    raise Exception(
                        f"SmartThings Authentication failed: {error_text}"
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
                        f"SmartThings API error {resp.status}: {error_text}"
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
        """Send remote command to device using SmartThings API.
        
        For Samsung TVs, we need to use the samsungvd.remoteControl capability
        with the 'send' command and the key code as argument.
        
        Note: SmartThings only supports a limited set of commands.
        Commands not in SMARTTHINGS_COMMANDS will be logged as unsupported.
        
        This method uses a lock to prevent command flooding and ensures
        a minimum delay between consecutive commands.
        """
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
        """Validate SmartThings token."""
        try:
            response = await self._request("GET", "/devices")
            is_valid = "items" in response
            LOGGER.debug(f"Token validation: {'success' if is_valid else 'failed'}")
            return is_valid
        except Exception as e:
            LOGGER.error(f"Token validation failed: {e}")
            return False

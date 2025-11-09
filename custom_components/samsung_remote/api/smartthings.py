"""SmartThings API client for Samsung devices."""

import asyncio
import json
from typing import Any, Optional

import aiohttp
from homeassistant.core import HomeAssistant

from ..const import LOGGER, DEFAULT_TIMEOUT, SAMSUNG_KEY_MAP


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

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close session."""
        if self.session and not self.session.closed:
            await self.session.close()

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
                if resp.status == 200 or resp.status == 201:
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

    async def get_devices(self) -> list[dict[str, Any]]:
        """Fetch all devices from SmartThings."""
        try:
            response = await self._request("GET", "/devices")
            devices = response.get("items", [])
            
            # Cache and filter for TV devices
            tv_devices = []
            for device in devices:
                if self._is_tv_device(device):
                    self.device_cache[device["deviceId"]] = device
                    tv_devices.append(device)
            
            return tv_devices
        except Exception as e:
            LOGGER.error(f"Failed to fetch devices: {e}")
            raise

    def _is_tv_device(self, device: dict[str, Any]) -> bool:
        """Check if device is a TV."""
        device_type = device.get("deviceType", "").lower()
        capabilities = [cap.get("id") for cap in device.get("components", [{}])[0].get("capabilities", [])]
        
        return "tv" in device_type or any(
            cap in capabilities for cap in ["remoteControl", "mediaPlayback", "tvChannel"]
        )

    async def send_command(self, device_id: str, command: str) -> bool:
        """Send remote command to device."""
        try:
            key = SAMSUNG_KEY_MAP.get(command, command)
            payload = {
                "commands": [
                    {
                        "component": "main",
                        "capability": "remoteControl",
                        "command": "sendCommand",
                        "arguments": [key],
                    }
                ]
            }
            
            await self._request("POST", f"/devices/{device_id}/commands", payload)
            LOGGER.debug(f"Sent command {command} to device {device_id}")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to send command {command}: {e}")
            return False

    async def validate_token(self) -> bool:
        """Validate SmartThings token."""
        try:
            response = await self._request("GET", "/devices")
            return "items" in response
        except Exception as e:
            LOGGER.error(f"Token validation failed: {e}")
            return False

"""SmartThings API handler for Samsung Remote."""
import logging
import aiohttp
from typing import Dict, Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from ..const import SMARTTHINGS_API_BASE, SMARTTHINGS_COMMANDS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmartThingsAPI:
    """Handle SmartThings API calls."""

    def __init__(self, hass: HomeAssistant, device_id: str, access_token: str = None):
        """Initialize the SmartThings API handler."""
        self.hass = hass
        self.device_id = device_id
        self._access_token = access_token
        self._session = None

    async def _ensure_token(self) -> str:
        """Ensure we have a valid access token."""
        if self._access_token:
            return self._access_token
        
        # Hole Token aus der SmartThings Integration
        smartthings_entries = self.hass.config_entries.async_entries("smartthings")
        
        if not smartthings_entries:
            raise ValueError("SmartThings integration not configured")
        
        st_entry = smartthings_entries[0]
        
        # Versuche Token aus verschiedenen Quellen
        if "token" in st_entry.data:
            token_data = st_entry.data["token"]
            if isinstance(token_data, dict):
                self._access_token = token_data.get("access_token")
        elif "access_token" in st_entry.data:
            self._access_token = st_entry.data["access_token"]
        
        # Wenn immer noch kein Token, nutze OAuth2 Session
        if not self._access_token:
            try:
                implementation = await config_entry_oauth2_flow.async_get_implementation(
                    self.hass, "smartthings"
                )
                
                if implementation:
                    session = config_entry_oauth2_flow.OAuth2Session(
                        self.hass, st_entry, implementation
                    )
                    
                    token_data = await session.async_ensure_token_valid()
                    if token_data:
                        self._access_token = token_data.get("access_token")
            except Exception as e:
                _LOGGER.error(f"Failed to get OAuth token: {e}")
                raise
        
        if not self._access_token:
            raise ValueError("Could not retrieve SmartThings access token")
        
        _LOGGER.debug("Successfully retrieved SmartThings access token")
        return self._access_token

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the SmartThings API."""
        token = await self._ensure_token()
        session = await self._get_session()
        
        url = f"{SMARTTHINGS_API_BASE}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        _LOGGER.debug(f"SmartThings API {method} request to {url}")
        
        try:
            async with session.request(
                method,
                url,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    _LOGGER.error("SmartThings API authentication failed. Token may be expired.")
                    raise ValueError("Authentication failed")
                
                if response.status >= 400:
                    _LOGGER.error(
                        f"SmartThings API error {response.status}: {response_text}"
                    )
                    raise ValueError(f"API error: {response.status}")
                
                if response_text:
                    return await response.json()
                return {}
                
        except aiohttp.ClientError as e:
            _LOGGER.error(f"SmartThings API connection error: {e}")
            raise

    async def get_device_status(self) -> Dict[str, Any]:
        """Get the current status of the device."""
        try:
            return await self._make_request("GET", f"devices/{self.device_id}/status")
        except Exception as e:
            _LOGGER.error(f"Failed to get device status: {e}")
            return {}

    async def send_command(self, command: str) -> bool:
        """Send a command to the device using SmartThings API."""
        # Mappe den Befehl auf SmartThings Command
        st_command = SMARTTHINGS_COMMANDS.get(command.upper())
        
        if not st_command:
            _LOGGER.warning(
                f"Command '{command}' is not supported by SmartThings API. "
                f"Supported commands: {', '.join(SMARTTHINGS_COMMANDS.keys())}"
            )
            return False
        
        _LOGGER.debug(f"Sending command '{command}' (mapped to '{st_command}') to device {self.device_id}")
        
        # Erstelle den Command Payload
        command_data = {
            "commands": [
                {
                    "component": "main",
                    "capability": "mediaPlaybackControl" if st_command in ["play", "pause", "stop", "rewind", "fastForward"] else "keypadInput",
                    "command": st_command,
                    "arguments": []
                }
            ]
        }
        
        try:
            result = await self._make_request(
                "POST",
                f"devices/{self.device_id}/commands",
                data=command_data
            )
            
            _LOGGER.debug(f"Command result: {result}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Failed to send command '{command}': {e}")
            return False

    async def send_key(self, key: str) -> bool:
        """Send a key press using the keypad input capability."""
        _LOGGER.debug(f"Sending key '{key}' to device {self.device_id}")
        
        command_data = {
            "commands": [
                {
                    "component": "main",
                    "capability": "keypadInput",
                    "command": "sendKey",
                    "arguments": [key]
                }
            ]
        }
        
        try:
            await self._make_request(
                "POST",
                f"devices/{self.device_id}/commands",
                data=command_data
            )
            return True
            
        except Exception as e:
            _LOGGER.error(f"Failed to send key '{key}': {e}")
            return False

    async def set_volume(self, volume: int) -> bool:
        """Set the volume level."""
        _LOGGER.debug(f"Setting volume to {volume} for device {self.device_id}")
        
        command_data = {
            "commands": [
                {
                    "component": "main",
                    "capability": "audioVolume",
                    "command": "setVolume",
                    "arguments": [volume]
                }
            ]
        }
        
        try:
            await self._make_request(
                "POST",
                f"devices/{self.device_id}/commands",
                data=command_data
            )
            return True
            
        except Exception as e:
            _LOGGER.error(f"Failed to set volume: {e}")
            return False

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get device capabilities."""
        try:
            return await self._make_request("GET", f"devices/{self.device_id}")
        except Exception as e:
            _LOGGER.error(f"Failed to get capabilities: {e}")
            return {}

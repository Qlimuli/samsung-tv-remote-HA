"""Remote platform for Samsung Remote integration."""
import logging
from typing import Any, Iterable

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONNECTION_METHOD_SMARTTHINGS,
    CONNECTION_METHOD_LOCAL,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
)
from .api.smartthings import SmartThingsAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Samsung Remote from a config entry."""
    connection_method = entry.data.get("connection_method")
    
    if connection_method == CONNECTION_METHOD_SMARTTHINGS:
        device_id = entry.data[CONF_DEVICE_ID]
        device_name = entry.data.get(CONF_DEVICE_NAME, "Samsung TV")
        access_token = entry.data.get("access_token")
        
        remote = SamsungSmartThingsRemote(
            hass, device_id, device_name, access_token
        )
    else:
        # Local Tizen implementation
        host = entry.data["host"]
        name = entry.data.get("name", "Samsung TV")
        remote = SamsungTizenRemote(hass, host, name)
    
    async_add_entities([remote])


class SamsungSmartThingsRemote(RemoteEntity):
    """Representation of a Samsung TV remote using SmartThings API."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        device_id: str, 
        device_name: str,
        access_token: str = None
    ):
        """Initialize the remote."""
        self._hass = hass
        self._device_id = device_id
        self._name = device_name
        self._api = SmartThingsAPI(hass, device_id, access_token)
        self._is_on = True
        self._attr_unique_id = f"{DOMAIN}_{device_id}"

    @property
    def name(self) -> str:
        """Return the name of the remote."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return True if the remote is on."""
        return self._is_on

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._name,
            "manufacturer": "Samsung",
            "model": "Smart TV",
            "via_device": (DOMAIN, self._device_id),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the remote on."""
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the remote off."""
        # SmartThings doesn't really turn off, just update state
        self._is_on = False
        self.async_write_ha_state()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the TV."""
        _LOGGER.debug(f"Sending commands: {command}")
        
        for cmd in command:
            try:
                result = await self._api.send_command(cmd)
                
                if result:
                    _LOGGER.info(f"Successfully sent command: {cmd}")
                else:
                    _LOGGER.warning(f"Command '{cmd}' may have failed")
                    
            except Exception as e:
                _LOGGER.error(f"Error sending command '{cmd}': {e}")

    async def async_update(self) -> None:
        """Update the remote state."""
        try:
            status = await self._api.get_device_status()
            
            # Prüfe ob das Gerät online ist
            if status:
                self._is_on = True
            
        except Exception as e:
            _LOGGER.debug(f"Failed to update remote state: {e}")


class SamsungTizenRemote(RemoteEntity):
    """Representation of a Samsung TV remote using local Tizen API."""

    def __init__(self, hass: HomeAssistant, host: str, name: str):
        """Initialize the remote."""
        self._hass = hass
        self._host = host
        self._name = name
        self._is_on = True
        self._attr_unique_id = f"{DOMAIN}_{host}"

    @property
    def name(self) -> str:
        """Return the name of the remote."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return True if the remote is on."""
        return self._is_on

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._name,
            "manufacturer": "Samsung",
            "model": "Smart TV (Local)",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the remote on."""
        await self.async_send_command(["POWER"])

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the remote off."""
        await self.async_send_command(["POWER"])

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the TV."""
        _LOGGER.debug(f"Sending local commands: {command}")
        
        # TODO: Implement local Tizen WebSocket connection
        # For now, log that local is not fully implemented
        _LOGGER.warning(
            "Local Tizen support is limited. "
            "For full functionality, use SmartThings API."
        )
        
        for cmd in command:
            _LOGGER.info(f"Would send local command: {cmd}")

    async def async_update(self) -> None:
        """Update the remote state."""
        # TODO: Implement ping or WebSocket check
        pass

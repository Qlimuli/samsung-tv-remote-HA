"""Remote entity for Samsung TV."""

from typing import Any, Optional

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.smartthings import SmartThingsAPI
from .api.tizen_local import TizenLocalAPI
from .const import DOMAIN, LOGGER, SUPPORTED_COMMANDS


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up remote entity."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    
    entity = SamsungRemote(
        hass=hass,
        config_entry=config_entry,
        api=data["api"],
        device_id=data["device_id"],
        device_name=data["device_name"],
    )
    
    async_add_entities([entity])


class SamsungRemote(RemoteEntity):
    """Samsung Smart TV remote entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: Any,
        device_id: str,
        device_name: str,
    ):
        """Initialize Samsung remote."""
        self.hass = hass
        self._config_entry = config_entry
        self._api = api
        self._device_id = device_id
        self._device_name = device_name
        self._attr_name = device_name
        self._attr_supported_features = 1  # SEND_COMMAND feature flag
        self._attr_unique_id = f"samsung_remote_{device_id}"
        self._attr_icon = "mdi:remote"

    @property
    def supported_features(self) -> int:
        """Return supported features."""
        return self._attr_supported_features

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Samsung",
            "model": "Smart TV",
        }

    async def async_send_command(
        self,
        command: list[str],
        frequency: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Send command to remote."""
        try:
            for cmd in command:
                success = await self._api.send_command(self._device_id, cmd)
                if not success:
                    LOGGER.warning(f"Command {cmd} may have failed for {self._device_name}")
        except Exception as e:
            LOGGER.error(f"Failed to send command: {e}")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "supported_commands": SUPPORTED_COMMANDS,
            "api_method": self._config_entry.data.get("api_method", "smartthings"),
        }

"""Remote entity for Samsung TV."""
import asyncio
from typing import Any, Iterable

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

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
        self._attr_unique_id = f"{device_id}_remote"
        self._attr_icon = "mdi:remote"
        self._attr_is_on = True  # Assume on by default
        self._attr_available = True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Samsung",
            "model": "Smart TV",
            "sw_version": None,
        }

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send command to remote."""
        num_repeats = kwargs.get("num_repeats", 1)
        delay = kwargs.get("delay_secs", 0.4)
        
        LOGGER.debug(f"Sending commands: {command}, repeats: {num_repeats}, delay: {delay}")
        
        try:
            for _ in range(num_repeats):
                for cmd in command:
                    if cmd not in SUPPORTED_COMMANDS:
                        LOGGER.warning(
                            f"Command '{cmd}' not in supported commands. "
                            f"Supported: {', '.join(SUPPORTED_COMMANDS)}"
                        )
                    
                    success = await self._api.send_command(self._device_id, cmd)
                    if not success:
                        LOGGER.warning(
                            f"Command {cmd} may have failed for {self._device_name}"
                        )
                    else:
                        LOGGER.debug(f"Successfully sent command: {cmd}")
                    
                    # Delay between commands
                    if len(list(command)) > 1 or num_repeats > 1:
                        await asyncio.sleep(delay)
                        
            self._attr_available = True
                        
        except Exception as e:
            LOGGER.error(f"Failed to send command: {e}", exc_info=True)
            self._attr_available = False
            raise

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        LOGGER.debug(f"Turning on {self._device_name}")
        await self.async_send_command(["POWER"])
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        LOGGER.debug(f"Turning off {self._device_name}")
        await self.async_send_command(["POWER"])
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "supported_commands": SUPPORTED_COMMANDS,
            "api_method": self._config_entry.data.get("api_method", "smartthings"),
            "device_id": self._device_id,
        }

    async def async_update(self) -> None:
        """Update the entity state."""
        # Most Samsung TVs don't provide reliable power state via API
        # Keeping entity available unless commands fail
        pass
    
    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()
        LOGGER.info(
            f"Samsung Remote entity added: {self._device_name} ({self._device_id})"
        )

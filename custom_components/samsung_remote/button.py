"""Button entities for Samsung TV commands."""
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER


BUTTON_COMMANDS = {
    "mute": {
        "command": "MUTE",
        "icon": "mdi:volume-mute",
        "translation_key": "mute",
    },
    "home": {
        "command": "HOME",
        "icon": "mdi:home",
        "translation_key": "home",
    },
    "menu": {
        "command": "MENU",
        "icon": "mdi:menu",
        "translation_key": "menu",
    },
    "back": {
        "command": "BACK",
        "icon": "mdi:arrow-left",
        "translation_key": "back",
    },
    "exit": {
        "command": "EXIT",
        "icon": "mdi:exit-to-app",
        "translation_key": "exit",
    },
    "up": {
        "command": "UP",
        "icon": "mdi:arrow-up-bold",
        "translation_key": "up",
    },
    "down": {
        "command": "DOWN",
        "icon": "mdi:arrow-down-bold",
        "translation_key": "down",
    },
    "left": {
        "command": "LEFT",
        "icon": "mdi:arrow-left-bold",
        "translation_key": "left",
    },
    "right": {
        "command": "RIGHT",
        "icon": "mdi:arrow-right-bold",
        "translation_key": "right",
    },
    "enter": {
        "command": "OK",
        "icon": "mdi:keyboard-return",
        "translation_key": "enter",
    },
    "play": {
        "command": "PLAY",
        "icon": "mdi:play",
        "translation_key": "play",
    },
    "pause": {
        "command": "PAUSE",
        "icon": "mdi:pause",
        "translation_key": "pause",
    },
    "stop": {
        "command": "STOP",
        "icon": "mdi:stop",
        "translation_key": "stop",
    },
    "rewind": {
        "command": "REWIND",
        "icon": "mdi:rewind",
        "translation_key": "rewind",
    },
    "fast_forward": {
        "command": "FF",
        "icon": "mdi:fast-forward",
        "translation_key": "fast_forward",
    },
    "play_back": {
        "command": "PLAY_BACK",
        "icon": "mdi:skip-backward",
        "translation_key": "play_back",
    },
    "source": {
        "command": "SOURCE",
        "icon": "mdi:video-input-hdmi",
        "translation_key": "source",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    
    buttons = [
        SamsungTVButton(
            hass=hass,
            config_entry=config_entry,
            api=data["api"],
            device_id=data["device_id"],
            device_name=data["device_name"],
            button_id=button_id,
            button_config=button_config,
        )
        for button_id, button_config in BUTTON_COMMANDS.items()
    ]
    
    async_add_entities(buttons)


class SamsungTVButton(ButtonEntity):
    """Representation of a Samsung TV button."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: Any,
        device_id: str,
        device_name: str,
        button_id: str,
        button_config: dict[str, str],
    ):
        """Initialize the button."""
        self.hass = hass
        self._config_entry = config_entry
        self._api = api
        self._device_id = device_id
        self._device_name = device_name
        self._button_id = button_id
        self._command = button_config["command"]
        self._attr_unique_id = f"{device_id}_{button_id}"
        self._attr_icon = button_config["icon"]
        self._attr_translation_key = button_config["translation_key"]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Samsung",
            "model": "Smart TV",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        LOGGER.debug(
            f"Button '{self._button_id}' pressed, sending command: {self._command}"
        )
        try:
            success = await self._api.send_command(self._device_id, self._command)
            if success:
                LOGGER.debug(
                    f"Successfully sent command {self._command} for button {self._button_id}"
                )
            else:
                LOGGER.warning(
                    f"Command {self._command} may have failed for button {self._button_id}"
                )
        except Exception as e:
            LOGGER.error(
                f"Failed to send command {self._command} for button {self._button_id}: {e}",
                exc_info=True,
            )
            raise

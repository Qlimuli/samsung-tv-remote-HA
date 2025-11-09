"""Button entities for Samsung TV commands."""
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER


BUTTON_COMMANDS = {
    "power": {
        "command": "POWER",
        "icon": "mdi:power",
        "translation_key": "power",
    },
    "poweroff": {
        "command": "POWEROFF",
        "icon": "mdi:power-off",
        "translation_key": "poweroff",
    },
    "volume_up": {
        "command": "VOLUP",
        "icon": "mdi:volume-plus",
        "translation_key": "volume_up",
    },
    "volume_down": {
        "command": "VOLDOWN",
        "icon": "mdi:volume-minus",
        "translation_key": "volume_down",
    },
    "mute": {
        "command": "MUTE",
        "icon": "mdi:volume-mute",
        "translation_key": "mute",
    },
    "channel_up": {
        "command": "CHUP",
        "icon": "mdi:chevron-up",
        "translation_key": "channel_up",
    },
    "channel_down": {
        "command": "CHDOWN",
        "icon": "mdi:chevron-down",
        "translation_key": "channel_down",
    },
    "previous_channel": {
        "command": "PRECH",
        "icon": "mdi:history",
        "translation_key": "previous_channel",
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
    "source": {
        "command": "SOURCE",
        "icon": "mdi:video-input-hdmi",
        "translation_key": "source",
    },
    "hdmi1": {
        "command": "HDMI1",
        "icon": "mdi:video-input-hdmi",
        "translation_key": "hdmi1",
    },
    "hdmi2": {
        "command": "HDMI2",
        "icon": "mdi:video-input-hdmi",
        "translation_key": "hdmi2",
    },
    "hdmi3": {
        "command": "HDMI3",
        "icon": "mdi:video-input-hdmi",
        "translation_key": "hdmi3",
    },
    "hdmi4": {
        "command": "HDMI4",
        "icon": "mdi:video-input-hdmi",
        "translation_key": "hdmi4",
    },
    "guide": {
        "command": "GUIDE",
        "icon": "mdi:television-guide",
        "translation_key": "guide",
    },
    "channel_list": {
        "command": "CH_LIST",
        "icon": "mdi:format-list-numbered",
        "translation_key": "channel_list",
    },
    "tools": {
        "command": "TOOLS",
        "icon": "mdi:tools",
        "translation_key": "tools",
    },
    "info": {
        "command": "INFO",
        "icon": "mdi:information",
        "translation_key": "info",
    },
    "settings": {
        "command": "SETTINGS",
        "icon": "mdi:cog",
        "translation_key": "settings",
    },
    "picture_mode": {
        "command": "PICTURE_MODE",
        "icon": "mdi:image-auto-adjust",
        "translation_key": "picture_mode",
    },
    "sound_mode": {
        "command": "SOUND_MODE",
        "icon": "mdi:speaker",
        "translation_key": "sound_mode",
    },
    "number_0": {
        "command": "NUM0",
        "icon": "mdi:numeric-0",
        "translation_key": "number_0",
    },
    "number_1": {
        "command": "NUM1",
        "icon": "mdi:numeric-1",
        "translation_key": "number_1",
    },
    "number_2": {
        "command": "NUM2",
        "icon": "mdi:numeric-2",
        "translation_key": "number_2",
    },
    "number_3": {
        "command": "NUM3",
        "icon": "mdi:numeric-3",
        "translation_key": "number_3",
    },
    "number_4": {
        "command": "NUM4",
        "icon": "mdi:numeric-4",
        "translation_key": "number_4",
    },
    "number_5": {
        "command": "NUM5",
        "icon": "mdi:numeric-5",
        "translation_key": "number_5",
    },
    "number_6": {
        "command": "NUM6",
        "icon": "mdi:numeric-6",
        "translation_key": "number_6",
    },
    "number_7": {
        "command": "NUM7",
        "icon": "mdi:numeric-7",
        "translation_key": "number_7",
    },
    "number_8": {
        "command": "NUM8",
        "icon": "mdi:numeric-8",
        "translation_key": "number_8",
    },
    "number_9": {
        "command": "NUM9",
        "icon": "mdi:numeric-9",
        "translation_key": "number_9",
    },
    "red": {
        "command": "RED",
        "icon": "mdi:alpha-r-circle",
        "translation_key": "red",
    },
    "green": {
        "command": "GREEN",
        "icon": "mdi:alpha-g-circle",
        "translation_key": "green",
    },
    "yellow": {
        "command": "YELLOW",
        "icon": "mdi:alpha-y-circle",
        "translation_key": "yellow",
    },
    "blue": {
        "command": "BLUE",
        "icon": "mdi:alpha-b-circle",
        "translation_key": "blue",
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

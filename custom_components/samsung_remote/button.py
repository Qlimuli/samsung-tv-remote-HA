"""Button platform for Samsung Remote integration."""
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONNECTION_METHOD_SMARTTHINGS,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    SMARTTHINGS_COMMANDS,
    TIZEN_KEYS,
)
from .api.smartthings import SmartThingsAPI

_LOGGER = logging.getLogger(__name__)

# Button definitions
BUTTONS = {
    "power": {"name": "Power", "icon": "mdi:power", "key": "POWER"},
    "home": {"name": "Home", "icon": "mdi:home", "key": "HOME"},
    "menu": {"name": "Menu", "icon": "mdi:menu", "key": "MENU"},
    "back": {"name": "Back", "icon": "mdi:arrow-left", "key": "BACK"},
    "up": {"name": "Up", "icon": "mdi:arrow-up", "key": "UP"},
    "down": {"name": "Down", "icon": "mdi:arrow-down", "key": "DOWN"},
    "left": {"name": "Left", "icon": "mdi:arrow-left", "key": "LEFT"},
    "right": {"name": "Right", "icon": "mdi:arrow-right", "key": "RIGHT"},
    "enter": {"name": "Enter", "icon": "mdi:check", "key": "ENTER"},
    "play": {"name": "Play", "icon": "mdi:play", "key": "PLAY"},
    "pause": {"name": "Pause", "icon": "mdi:pause", "key": "PAUSE"},
    "stop": {"name": "Stop", "icon": "mdi:stop", "key": "STOP"},
    "volume_up": {"name": "Volume Up", "icon": "mdi:volume-plus", "key": "VOLUME_UP"},
    "volume_down": {"name": "Volume Down", "icon": "mdi:volume-minus", "key": "VOLUME_DOWN"},
    "mute": {"name": "Mute", "icon": "mdi:volume-mute", "key": "MUTE"},
    "channel_up": {"name": "Channel Up", "icon": "mdi:arrow-up-bold", "key": "CHANNEL_UP"},
    "channel_down": {"name": "Channel Down", "icon": "mdi:arrow-down-bold", "key": "CHANNEL_DOWN"},
    "source": {"name": "Source", "icon": "mdi:hdmi-port", "key": "SOURCE"},
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Samsung Remote buttons from a config entry."""
    connection_method = entry.data.get("connection_method")
    
    buttons = []
    
    if connection_method == CONNECTION_METHOD_SMARTTHINGS:
        device_id = entry.data[CONF_DEVICE_ID]
        device_name = entry.data.get(CONF_DEVICE_NAME, "Samsung TV")
        access_token = entry.data.get("access_token")
        
        for button_id, button_config in BUTTONS.items():
            buttons.append(
                SamsungSmartThingsButton(
                    hass,
                    device_id,
                    device_name,
                    button_id,
                    button_config,
                    access_token,
                )
            )
    else:
        # Local Tizen buttons
        host = entry.data["host"]
        name = entry.data.get("name", "Samsung TV")
        
        for button_id, button_config in BUTTONS.items():
            buttons.append(
                SamsungTizenButton(
                    hass,
                    host,
                    name,
                    button_id,
                    button_config,
                )
            )
    
    async_add_entities(buttons)


class SamsungSmartThingsButton(ButtonEntity):
    """Representation of a Samsung TV button using SmartThings API."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        device_name: str,
        button_id: str,
        button_config: dict,
        access_token: str = None,
    ):
        """Initialize the button."""
        self._hass = hass
        self._device_id = device_id
        self._device_name = device_name
        self._button_id = button_id
        self._button_config = button_config
        self._api = SmartThingsAPI(hass, device_id, access_token)
        
        self._attr_name = f"{device_name} {button_config['name']}"
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{button_id}"
        self._attr_icon = button_config.get("icon")

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Samsung",
            "model": "Smart TV",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        key = self._button_config["key"]
        
        _LOGGER.debug(f"Button '{self._button_id}' pressed, sending command '{key}'")
        
        try:
            # Prüfe ob der Befehl in SmartThings unterstützt wird
            if key.upper() in SMARTTHINGS_COMMANDS:
                result = await self._api.send_command(key)
                
                if not result:
                    _LOGGER.warning(
                        f"Command {key} may have failed for button {self._button_id}"
                    )
            else:
                # Versuche als direkten Key zu senden
                tizen_key = TIZEN_KEYS.get(key.upper())
                if tizen_key:
                    result = await self._api.send_key(tizen_key)
                    
                    if not result:
                        _LOGGER.warning(
                            f"Key {tizen_key} may have failed for button {self._button_id}"
                        )
                else:
                    _LOGGER.error(
                        f"Command '{key}' is not supported. "
                        f"This command may only work with Tizen Local API."
                    )
                    
        except Exception as e:
            _LOGGER.error(f"Error pressing button '{self._button_id}': {e}")


class SamsungTizenButton(ButtonEntity):
    """Representation of a Samsung TV button using local Tizen API."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        name: str,
        button_id: str,
        button_config: dict,
    ):
        """Initialize the button."""
        self._hass = hass
        self._host = host
        self._name = name
        self._button_id = button_id
        self._button_config = button_config
        
        self._attr_name = f"{name} {button_config['name']}"
        self._attr_unique_id = f"{DOMAIN}_{host}_{button_id}"
        self._attr_icon = button_config.get("icon")

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._name,
            "manufacturer": "Samsung",
            "model": "Smart TV (Local)",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        key = self._button_config["key"]
        tizen_key = TIZEN_KEYS.get(key.upper(), key)
        
        _LOGGER.debug(
            f"Button '{self._button_id}' pressed, would send local key '{tizen_key}'"
        )
        
        # TODO: Implement local Tizen WebSocket connection
        _LOGGER.warning(
            "Local Tizen support is limited. "
            "For full functionality, use SmartThings API."
        )

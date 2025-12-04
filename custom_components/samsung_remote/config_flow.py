"""Config flow for Samsung Remote integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONNECTION_METHOD_SMARTTHINGS = "smartthings"
CONNECTION_METHOD_LOCAL = "local"


class SamsungRemoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Remote."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.connection_method = None
        self.device_id = None
        self.device_name = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step - choose connection method."""
        if user_input is not None:
            self.connection_method = user_input["connection_method"]
            
            if self.connection_method == CONNECTION_METHOD_SMARTTHINGS:
                return await self.async_step_smartthings()
            else:
                return await self.async_step_local()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("connection_method", default=CONNECTION_METHOD_SMARTTHINGS): vol.In({
                    CONNECTION_METHOD_SMARTTHINGS: "SmartThings API (Recommended - Cloud-based)",
                    CONNECTION_METHOD_LOCAL: "Local Tizen (Fallback - Direct network)"
                })
            }),
            description_placeholders={
                "info": "SmartThings API requires the native SmartThings integration to be configured first."
            }
        )

    async def async_step_smartthings(self, user_input=None):
        """Handle SmartThings API setup."""
        errors = {}

        # Prüfe ob SmartThings Integration konfiguriert ist
        smartthings_entries = self.hass.config_entries.async_entries("smartthings")
        
        if not smartthings_entries:
            errors["base"] = "smartthings_not_configured"
            return self.async_show_form(
                step_id="smartthings",
                data_schema=vol.Schema({}),
                errors=errors,
                description_placeholders={
                    "error_info": (
                        "SmartThings integration not found!\n\n"
                        "Please set up the native SmartThings integration first:\n"
                        "1. Go to Settings > Devices & Services\n"
                        "2. Click 'Add Integration'\n"
                        "3. Search for 'SmartThings'\n"
                        "4. Complete the OAuth setup\n"
                        "5. Then return here to add Samsung Remote"
                    )
                }
            )

        if user_input is not None:
            # Hole die verfügbaren Samsung TVs aus SmartThings
            try:
                devices = await self._get_smartthings_devices()
                
                if not devices:
                    errors["base"] = "no_devices"
                    return self.async_show_form(
                        step_id="smartthings",
                        data_schema=vol.Schema({
                            vol.Required("refresh"): bool
                        }),
                        errors=errors,
                        description_placeholders={
                            "info": "No Samsung TVs found in your SmartThings account."
                        }
                    )
                
                self.device_id = user_input.get("device_id")
                self.device_name = user_input.get("device_name")
                
                if self.device_id:
                    # Erstelle den Config Entry
                    return self.async_create_entry(
                        title=self.device_name or "Samsung TV",
                        data={
                            "connection_method": CONNECTION_METHOD_SMARTTHINGS,
                            "device_id": self.device_id,
                            "device_name": self.device_name,
                        }
                    )
                    
            except Exception as e:
                _LOGGER.exception("Error setting up SmartThings connection")
                errors["base"] = "cannot_connect"

        # Hole die verfügbaren Geräte
        devices = await self._get_smartthings_devices()
        
        if not devices:
            return self.async_show_form(
                step_id="smartthings",
                data_schema=vol.Schema({}),
                errors={"base": "no_devices"},
                description_placeholders={
                    "info": "No Samsung TVs found. Make sure your TV is added to SmartThings."
                }
            )

        device_schema = vol.Schema({
            vol.Required("device_id"): vol.In({
                device["deviceId"]: f"{device['label']} ({device['deviceId']})"
                for device in devices
            }),
        })

        return self.async_show_form(
            step_id="smartthings",
            data_schema=device_schema,
            errors=errors,
            description_placeholders={
                "info": "Select your Samsung TV from the list of SmartThings devices."
            }
        )

    async def async_step_local(self, user_input=None):
        """Handle local Tizen setup."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input.get(CONF_NAME, "Samsung TV")

            # Prüfe ob die IP bereits konfiguriert ist
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # TODO: Teste die Verbindung zum TV
            # For now, we'll just create the entry
            
            return self.async_create_entry(
                title=name,
                data={
                    "connection_method": CONNECTION_METHOD_LOCAL,
                    CONF_HOST: host,
                    CONF_NAME: name,
                }
            )

        return self.async_show_form(
            step_id="local",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default="Samsung TV"): str,
            }),
            errors=errors,
            description_placeholders={
                "info": "Enter your TV's IP address. You can find this in your TV's network settings."
            }
        )

    async def _get_smartthings_devices(self):
        """Get Samsung TV devices from SmartThings."""
        try:
            # Hole die SmartThings Integration
            smartthings_entries = self.hass.config_entries.async_entries("smartthings")
            
            if not smartthings_entries:
                _LOGGER.error("No SmartThings integration configured")
                return []
            
            # Hole das erste SmartThings Entry
            st_entry = smartthings_entries[0]
            
            # Versuche das Token zu bekommen
            token = None
            
            if "token" in st_entry.data:
                token_data = st_entry.data["token"]
                if isinstance(token_data, dict):
                    token = token_data.get("access_token")
            elif "access_token" in st_entry.data:
                token = st_entry.data["access_token"]
            
            # Wenn kein Token, versuche OAuth2 Session
            if not token:
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
                            token = token_data.get("access_token")
                except Exception as e:
                    _LOGGER.error(f"Failed to get OAuth token: {e}")
            
            if not token:
                _LOGGER.error("Could not retrieve SmartThings token")
                return []
            
            # Importiere die SmartThings API
            import aiohttp
            
            # Hole die Geräte
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.smartthings.com/v1/devices",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Failed to get devices: {response.status}")
                        return []
                    
                    data = await response.json()
                    devices = data.get("items", [])
                    
                    # Filtere nur Samsung TVs
                    tv_devices = [
                        device for device in devices
                        if any(cap in device.get("capabilities", []) 
                               for cap in ["mediaPlayback", "tvChannel", "audioVolume"])
                    ]
                    
                    _LOGGER.info(f"Found {len(tv_devices)} Samsung TV(s)")
                    return tv_devices
                    
        except Exception as e:
            _LOGGER.exception("Error getting SmartThings devices")
            return []

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SamsungRemoteOptionsFlow(config_entry)


class SamsungRemoteOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Samsung Remote."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        connection_method = self.config_entry.data.get("connection_method")
        
        if connection_method == CONNECTION_METHOD_SMARTTHINGS:
            # SmartThings Options
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Optional(
                        "refresh_token_on_start",
                        default=self.config_entry.options.get("refresh_token_on_start", True)
                    ): bool,
                })
            )
        else:
            # Local Tizen Options
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({
                    vol.Optional(
                        "scan_interval",
                        default=self.config_entry.options.get("scan_interval", 30)
                    ): int,
                })
            )

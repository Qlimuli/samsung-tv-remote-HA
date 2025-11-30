"""Config flow for Samsung Remote integration."""

from typing import Any, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api.smartthings import SmartThingsAPI
from .api.tizen_local import TizenLocalAPI
from .const import (
    CONF_API_METHOD,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_LOCAL_IP,
    CONF_LOCAL_PSK,
    DEFAULT_API_METHOD,
    DOMAIN,
    LOGGER,
)


async def get_smartthings_token(hass: HomeAssistant) -> str | None:
    """Get SmartThings API token from existing SmartThings integration."""
    if "smartthings" not in hass.data:
        return None
    
    for entry in hass.config_entries.async_entries("smartthings"):
        if entry.data.get("access_token"):
            return entry.data["access_token"]
    
    return None


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Remote."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        """Initialize config flow."""
        self.api_method = DEFAULT_API_METHOD
        self.smartthings_api: Optional[SmartThingsAPI] = None
        self.devices: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.api_method = user_input[CONF_API_METHOD]

            if self.api_method == "smartthings":
                return await self.async_step_smartthings()
            else:
                return await self.async_step_tizen_local()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_METHOD, default=DEFAULT_API_METHOD
                    ): vol.In(["smartthings", "tizen_local"]),
                }
            ),
            errors=errors,
            description_placeholders={
                "info": "Choose your connection method.\n\n"
                "SmartThings: Uses the native Home Assistant SmartThings integration.\n"
                "Tizen Local: Direct connection to TV via local network."
            },
        )

    async def async_step_smartthings(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle SmartThings API setup."""
        errors: dict[str, str] = {}

        # Check if SmartThings integration exists
        token = await get_smartthings_token(self.hass)
        
        if not token:
            return self.async_abort(
                reason="smartthings_not_configured",
                description_placeholders={
                    "info": "The native SmartThings integration is not set up.\n\n"
                    "Please set it up first:\n"
                    "1. Go to Settings > Devices & Services\n"
                    "2. Click 'Add Integration'\n"
                    "3. Search for 'SmartThings'\n"
                    "4. Follow the setup instructions\n"
                    "5. Then come back to add this Samsung Remote integration"
                }
            )

        if user_input is not None or True:  # Auto-proceed since we have token
            try:
                LOGGER.info("Using existing SmartThings integration token")
                
                self.smartthings_api = SmartThingsAPI(self.hass, token=token)

                # Validate token
                if not await self.smartthings_api.validate_token():
                    errors["base"] = "invalid_token"
                    LOGGER.error("Token validation failed")
                else:
                    # Fetch devices
                    LOGGER.info("Token validation successful, fetching devices...")
                    try:
                        self.devices = await self.smartthings_api.get_devices()
                    except Exception as e:
                        LOGGER.warning(f"Could not fetch devices: {e}")
                        self.devices = []

                    if not self.devices:
                        return self.async_abort(
                            reason="no_devices_found",
                            description_placeholders={
                                "info": "No Samsung TVs found in your SmartThings account.\n\n"
                                "Make sure your TV is:\n"
                                "1. Connected to the same Samsung account\n"
                                "2. Powered on and connected to the network\n"
                                "3. Visible in the SmartThings mobile app"
                            }
                        )
                        
                    LOGGER.info(f"SmartThings setup successful. Found {len(self.devices)} devices")

                    # Clean up API before proceeding
                    await self.smartthings_api.close()
                    return await self.async_step_select_device()

            except Exception as e:
                LOGGER.error(f"SmartThings validation error: {e}", exc_info=True)
                errors["base"] = "connection_error"
            finally:
                if errors and self.smartthings_api:
                    await self.smartthings_api.close()

        return self.async_show_form(
            step_id="smartthings",
            data_schema=vol.Schema({}),  # No input needed
            errors=errors,
            description_placeholders={
                "info": "Using token from native SmartThings integration.\n\n"
                "Click Submit to discover your Samsung TVs."
            },
        )

    async def async_step_tizen_local(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle local Tizen setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                ip = user_input[CONF_LOCAL_IP].strip()
                psk = user_input.get(CONF_LOCAL_PSK, "").strip()
                device_name = user_input.get(CONF_DEVICE_NAME, f"Samsung TV {ip}").strip()

                if not ip:
                    errors["base"] = "invalid_ip"
                else:
                    api = TizenLocalAPI(ip, psk)
                    if not await api.validate_connection():
                        errors["base"] = "connection_failed"
                    else:
                        await api.close()
                        return await self._async_create_entry(
                            device_name=device_name,
                            device_id=ip.replace(".", "_"),
                            api_method="tizen_local",
                            local_ip=ip,
                            local_psk=psk,
                        )
            except Exception as e:
                LOGGER.error(f"Tizen validation error: {e}")
                errors["base"] = "connection_error"

        return self.async_show_form(
            step_id="tizen_local",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOCAL_IP): str,
                    vol.Optional(CONF_LOCAL_PSK, default=""): str,
                    vol.Optional(CONF_DEVICE_NAME, default="Samsung TV"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "ip_help": "Enter the IP address of your Samsung TV.\n\n"
                "You can find this in:\n"
                "TV Settings > Network > Network Status > IP Address"
            },
        )

    async def async_step_select_device(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle device selection."""
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device = next(
                (d for d in self.devices if d["deviceId"] == device_id), None
            )

            if device:
                return await self._async_create_entry(
                    device_name=device.get("label", device_id),
                    device_id=device_id,
                    api_method="smartthings",
                )

        if not self.devices:
            return self.async_abort(reason="no_devices_found")

        device_options = {
            d["deviceId"]: d.get("label", d["deviceId"]) for d in self.devices
        }

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE_ID): vol.In(device_options)}
            ),
            description_placeholders={
                "device_count": str(len(self.devices)),
                "info": f"Found {len(self.devices)} Samsung TV(s) in your SmartThings account.\n\n"
                "Select the TV you want to control:"
            },
        )

    async def _async_create_entry(self, **kwargs: Any) -> FlowResult:
        """Create config entry."""
        device_id = kwargs[CONF_DEVICE_ID]

        # Check if already configured
        await self.async_set_unique_id(device_id)
        self._abort_if_unique_id_configured()

        entry_data = {
            CONF_DEVICE_ID: device_id,
            CONF_DEVICE_NAME: kwargs[CONF_DEVICE_NAME],
            CONF_API_METHOD: kwargs[CONF_API_METHOD],
        }

        # Add method-specific data
        if kwargs[CONF_API_METHOD] == "tizen_local":
            entry_data[CONF_LOCAL_IP] = kwargs.get(CONF_LOCAL_IP)
            entry_data[CONF_LOCAL_PSK] = kwargs.get(CONF_LOCAL_PSK, "")

        return self.async_create_entry(
            title=kwargs[CONF_DEVICE_NAME],
            data=entry_data,
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Samsung Remote."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        api_method = self.config_entry.data.get(CONF_API_METHOD, "smartthings")

        if api_method == "smartthings":
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema({}),
                description_placeholders={
                    "info": "This integration uses the native SmartThings integration.\n\n"
                    "To update settings, please reconfigure the SmartThings integration:\n"
                    "Settings > Devices & Services > SmartThings > Configure"
                },
            )
        else:
            # Tizen local options
            errors: dict[str, str] = {}
            
            if user_input is not None:
                ip = user_input.get(CONF_LOCAL_IP, "").strip()
                psk = user_input.get(CONF_LOCAL_PSK, "").strip()

                if ip:
                    try:
                        api = TizenLocalAPI(ip, psk)
                        if await api.validate_connection():
                            await api.close()
                            # Update config entry
                            self.hass.config_entries.async_update_entry(
                                self.config_entry,
                                data={
                                    **self.config_entry.data,
                                    CONF_LOCAL_IP: ip,
                                    CONF_LOCAL_PSK: psk,
                                },
                            )
                            return self.async_create_entry(title="", data={})
                        else:
                            errors["base"] = "connection_failed"
                            await api.close()
                    except Exception as e:
                        LOGGER.error(f"Connection validation error: {e}")
                        errors["base"] = "connection_error"

            current_ip = self.config_entry.data.get(CONF_LOCAL_IP, "")
            current_psk = self.config_entry.data.get(CONF_LOCAL_PSK, "")

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_LOCAL_IP,
                            description={"suggested_value": current_ip},
                        ): str,
                        vol.Optional(
                            CONF_LOCAL_PSK,
                            description={"suggested_value": current_psk},
                        ): str,
                    }
                ),
                errors=errors,
                description_placeholders={
                    "info": "Update your TV's IP address or PSK if needed."
                },
            )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidToken(HomeAssistantError):
    """Error to indicate invalid token."""

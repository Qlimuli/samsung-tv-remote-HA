"""Config flow for Samsung Remote integration."""

import time
from typing import Any, Optional

import voluptuous as vol
from aiohttp import ClientConnectorDNSError

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api.smartthings import SmartThingsAPI
from .api.tizen_local import TizenLocalAPI
from .const import (
    CONF_API_METHOD,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_LOCAL_IP,
    CONF_LOCAL_PSK,
    CONF_SMARTTHINGS_TOKEN,
    CONF_ST_DEVICE,
    DEFAULT_API_METHOD,
    DOMAIN,
    LOGGER,
)


def get_smartthings_token(hass: HomeAssistant) -> str | None:
    """Get SmartThings API token from existing SmartThings integration."""
    # Check if SmartThings integration is loaded
    if "smartthings" not in hass.data:
        return None
    
    # Try to get token from SmartThings integration
    smartthings_data = hass.data.get("smartthings", {})
    
    # The token is usually stored in the config entry
    for entry in hass.config_entries.async_entries("smartthings"):
        if entry.data.get("access_token"):
            return entry.data["access_token"]
    
    return None


def get_smartthings_entries(hass: HomeAssistant) -> dict[str, str]:
    """Get list of SmartThings config entries."""
    entries = {}
    for entry in hass.config_entries.async_entries("smartthings"):
        entries[entry.entry_id] = entry.title
    return entries


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
        self.smartthings_token: Optional[str] = None
        self.use_existing_st: bool = False

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
                "info": "Choose your connection method"
            },
        )

    async def async_step_smartthings(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle SmartThings API setup."""
        errors: dict[str, str] = {}

        # Check if SmartThings integration exists
        st_entries = get_smartthings_entries(self.hass)
        existing_token = get_smartthings_token(self.hass)

        if user_input is not None:
            try:
                # Check if user wants to use existing SmartThings integration
                use_existing = user_input.get("use_existing_smartthings", False)
                
                if use_existing and existing_token:
                    token = existing_token
                    self.use_existing_st = True
                    LOGGER.info("Using token from existing SmartThings integration")
                else:
                    # User provides manual token
                    token = user_input.get(CONF_SMARTTHINGS_TOKEN, "").strip()
                    self.use_existing_st = False
                
                if not token:
                    errors["base"] = "invalid_token"
                    LOGGER.error("Token is empty")
                    raise ValueError("Token is required")

                # Check token length and format
                if len(token) < 10:
                    errors["base"] = "invalid_token"
                    LOGGER.error(f"Token too short (length: {len(token)})")
                    raise ValueError("Token appears to be invalid (too short)")

                LOGGER.info(f"Validating SmartThings token (length: {len(token)}, first 20: {token[:20]}...)")
                
                self.smartthings_api = SmartThingsAPI(
                    self.hass,
                    token=token,
                )

                # Validate token
                LOGGER.info("Starting token validation...")
                if not await self.smartthings_api.validate_token():
                    errors["base"] = "invalid_token" 
                    LOGGER.error(f"Token validation failed for token: {token[:20]}...")
                else:
                    # Fetch devices
                    LOGGER.info("Token validation successful, fetching devices...")
                    try:
                        self.devices = await self.smartthings_api.get_devices()
                    except Exception as e:
                        LOGGER.warning(f"Could not fetch devices during setup: {e}")
                        self.devices = []

                    # Store token
                    self.smartthings_token = token
                        
                    LOGGER.info(f"SmartThings setup successful. Found {len(self.devices)} devices")

                    # Clean up API before proceeding
                    await self.smartthings_api.close()
                    return await self.async_step_select_device()

            except ClientConnectorDNSError:
                LOGGER.error("DNS/Network error during SmartThings setup")
                errors["base"] = "connection_error"
            except Exception as e:
                LOGGER.error(f"SmartThings validation error: {e}", exc_info=True)
                errors["base"] = "connection_error"
            finally:
                if errors and self.smartthings_api:
                    await self.smartthings_api.close()

        # Build form schema
        schema = {}
        
        # If SmartThings integration exists, offer to use it
        if existing_token:
            schema[vol.Optional("use_existing_smartthings", default=True)] = bool
            description = (
                "✅ SmartThings Integration found!\n\n"
                "You can use your existing SmartThings integration\n"
                "or manually enter a token.\n\n"
                "Select 'Use existing SmartThings' to automatically\n"
                "use the token from your SmartThings integration."
            )
        else:
            description = (
                "⚠️ No SmartThings Integration found!\n\n"
                "Please install and configure the SmartThings integration first,\n"
                "or manually enter a Personal Access Token.\n\n"
                "To install SmartThings:\n"
                "1. Go to Settings → Devices & Services\n"
                "2. Click '+ Add Integration'\n"
                "3. Search for 'SmartThings'\n"
                "4. Follow the setup steps\n\n"
                "Or manually create a token at:\n"
                "https://account.smartthings.com/tokens"
            )
        
        # Always show manual token field (optional if SmartThings exists)
        if existing_token:
            schema[vol.Optional(CONF_SMARTTHINGS_TOKEN)] = str
        else:
            schema[vol.Required(CONF_SMARTTHINGS_TOKEN)] = str

        return self.async_show_form(
            step_id="smartthings",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={
                "token_help": description
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
                "ip_help": "Enter the IP address of your Samsung TV."
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
                    smartthings_token=self.smartthings_token,
                    use_existing_st=self.use_existing_st,
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
                "device_count": str(len(self.devices))
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
        if kwargs[CONF_API_METHOD] == "smartthings":
            # Only store token if not using existing SmartThings integration
            if not kwargs.get("use_existing_st", False):
                entry_data[CONF_SMARTTHINGS_TOKEN] = kwargs.get(CONF_SMARTTHINGS_TOKEN)
            else:
                # Mark that we're using existing SmartThings
                entry_data["use_existing_smartthings"] = True
        else:
            entry_data[CONF_LOCAL_IP] = kwargs.get(CONF_LOCAL_IP)
            entry_data[CONF_LOCAL_PSK] = kwargs.get(CONF_LOCAL_PSK, "")

        title = kwargs[CONF_DEVICE_NAME]
        if kwargs[CONF_API_METHOD] == "smartthings":
            if kwargs.get("use_existing_st", False):
                title += " (SmartThings Integration)"
            else:
                title += " (SmartThings)"

        return self.async_create_entry(
            title=title,
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
        errors: dict[str, str] = {}

        api_method = self.config_entry.data.get(CONF_API_METHOD, "smartthings")
        use_existing_st = self.config_entry.data.get("use_existing_smartthings", False)

        if user_input is not None:
            # Update based on API method
            if api_method == "smartthings":
                if not use_existing_st:
                    # Only allow token update if not using existing SmartThings
                    token = user_input.get(CONF_SMARTTHINGS_TOKEN, "").strip()

                    if token:
                        # Validate new token
                        try:
                            api = SmartThingsAPI(self.hass, token=token)
                            if await api.validate_token():
                                await api.close()
                                # Update config entry with new token
                                new_data = {**self.config_entry.data}
                                new_data[CONF_SMARTTHINGS_TOKEN] = token
                                self.hass.config_entries.async_update_entry(
                                    self.config_entry,
                                    data=new_data,
                                )
                                return self.async_create_entry(title="", data={})
                            else:
                                errors["base"] = "invalid_token"
                                await api.close()
                        except Exception as e:
                            LOGGER.error(f"Token validation error: {e}")
                            errors["base"] = "connection_error"
                else:
                    # Using existing SmartThings - nothing to update
                    return self.async_create_entry(title="", data={})
            else:
                # Tizen local options
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

        # Show form based on API method
        if api_method == "smartthings":
            if use_existing_st:
                # Using existing SmartThings - show info only
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema({}),
                    description_placeholders={
                        "current_method": "SmartThings Integration",
                        "info": "✅ Using existing SmartThings integration\n\n"
                        "Token is managed by the SmartThings integration.\n"
                        "No configuration needed here.\n\n"
                        "To update token, go to:\n"
                        "Settings → Devices & Services → SmartThings",
                    },
                )
            else:
                current_token = self.config_entry.data.get(CONF_SMARTTHINGS_TOKEN, "")
                
                # Show masked token for security
                masked_token = (
                    f"{'*' * (len(current_token) - 8)}{current_token[-8:]}"
                    if len(current_token) > 8
                    else "***"
                )

                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                CONF_SMARTTHINGS_TOKEN,
                                description={"suggested_value": masked_token},
                            ): str,
                        }
                    ),
                    errors=errors,
                    description_placeholders={
                        "current_method": "SmartThings API",
                        "info": f"Update your Personal Access Token\n\n"
                        f"Current Token: {masked_token}\n\n"
                        f"Get a new token at:\nhttps://account.smartthings.com/tokens",
                    },
                )
        else:
            # Tizen local options
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
                    "current_method": "Local Tizen Connection",
                    "info": "Update IP address or PSK.",
                },
            )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidToken(HomeAssistantError):
    """Error to indicate invalid token."""

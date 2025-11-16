"""Config flow for Samsung Remote integration."""

import time
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
    CONF_SMARTTHINGS_ACCESS_TOKEN,
    CONF_SMARTTHINGS_REFRESH_TOKEN,
    CONF_SMARTTHINGS_TOKEN,
    CONF_SMARTTHINGS_TOKEN_EXPIRES,
    DEFAULT_API_METHOD,
    DOMAIN,
    LOGGER,
)


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
        self.smartthings_access_token: Optional[str] = None
        self.smartthings_refresh_token: Optional[str] = None
        self.smartthings_token_expires: Optional[float] = None

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

        if user_input is not None:
            try:
                access_token = user_input[CONF_SMARTTHINGS_ACCESS_TOKEN].strip()
                refresh_token = user_input.get(CONF_SMARTTHINGS_REFRESH_TOKEN, "").strip()
                
                if not access_token:
                    errors["base"] = "invalid_token"
                    LOGGER.error("Access token is empty")
                    raise ValueError("Access token is required")

                # Check token length and format
                if len(access_token) < 10:
                    errors["base"] = "invalid_token"
                    LOGGER.error(f"Access token too short (length: {len(access_token)})")
                    raise ValueError("Access token appears to be invalid (too short)")

                # Check for common invalid characters
                if any(char in access_token for char in ['\n', '\r', '\t', '  ']):
                    errors["base"] = "invalid_token"
                    LOGGER.error("Access token contains invalid whitespace characters")
                    raise ValueError("Access token contains invalid whitespace")

                LOGGER.info(f"Validating SmartThings token (length: {len(access_token)}, first 20: {access_token[:20]}...)")
                
                self.smartthings_api = SmartThingsAPI(
                    self.hass,
                    access_token=access_token,
                    refresh_token=refresh_token if refresh_token else None,
                    token_expires=time.time() + 86400,
                )

                # Validate tokens
                LOGGER.info("Starting token validation...")
                if not await self.smartthings_api.validate_token():
                    errors["base"] = "invalid_token"
                    LOGGER.error(f"Token validation failed for token: {access_token[:20]}...")
                else:
                    # Fetch devices
                    LOGGER.info("Token validation successful, fetching devices...")
                    self.devices = await self.smartthings_api.get_devices()
                    if not self.devices:
                        errors["base"] = "no_devices_found"
                        LOGGER.warning("No devices found in SmartThings account")
                    else:
                        # If validation succeeded, store tokens
                        self.smartthings_access_token = access_token
                        self.smartthings_refresh_token = refresh_token if refresh_token else None
                        self.smartthings_token_expires = time.time() + 86400
                        
                        LOGGER.info(f"SmartThings validation successful. Found {len(self.devices)} devices")

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
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SMARTTHINGS_ACCESS_TOKEN): str,
                    vol.Optional(CONF_SMARTTHINGS_REFRESH_TOKEN): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "token_help": "SmartThings OAuth Setup:\n"
                "1. Access Token: Your current OAuth access token (expires in 24 hours)\n"
                "2. Refresh Token: Your OAuth refresh token (used to automatically renew access token)\n\n"
                "IMPORTANT TROUBLESHOOTING:\n"
                "- Verify tokens are EXACTLY correct (copy/paste from SmartThings)\n"
                "- NO leading or trailing spaces\n"
                "- NO newlines or tabs\n"
                "- Check token length (usually 40+ characters)\n"
                "- Ensure TV is in your SmartThings account\n"
                "- Check token hasn't expired\n\n"
                "If you still get 'invalid_token':\n"
                "1. Check the Home Assistant logs for token details\n"
                "2. Generate a new access token from SmartThings\n"
                "3. Verify in SmartThings that your TV is properly connected\n\n"
                "See documentation for detailed setup instructions."
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
                "ip_help": "Enter the IP address of your Samsung TV. No token expiration - tokens are permanent."
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
                    smartthings_access_token=self.smartthings_access_token,
                    smartthings_refresh_token=self.smartthings_refresh_token,
                    smartthings_token_expires=self.smartthings_token_expires,
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
            entry_data[CONF_SMARTTHINGS_ACCESS_TOKEN] = kwargs.get(
                CONF_SMARTTHINGS_ACCESS_TOKEN
            )
            entry_data[CONF_SMARTTHINGS_REFRESH_TOKEN] = kwargs.get(
                CONF_SMARTTHINGS_REFRESH_TOKEN
            )
            entry_data[CONF_SMARTTHINGS_TOKEN_EXPIRES] = kwargs.get(
                CONF_SMARTTHINGS_TOKEN_EXPIRES
            )
            # Keep old token format for backward compatibility
            entry_data[CONF_SMARTTHINGS_TOKEN] = kwargs.get(
                CONF_SMARTTHINGS_ACCESS_TOKEN
            )
        else:
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
        errors: dict[str, str] = {}

        api_method = self.config_entry.data.get(CONF_API_METHOD, "smartthings")

        if user_input is not None:
            # Update based on API method
            if api_method == "smartthings":
                access_token = user_input.get(CONF_SMARTTHINGS_ACCESS_TOKEN, "").strip()
                refresh_token = user_input.get(CONF_SMARTTHINGS_REFRESH_TOKEN, "").strip()

                if access_token:
                    # Validate new tokens
                    try:
                        api = SmartThingsAPI(
                            self.hass,
                            access_token=access_token,
                            refresh_token=refresh_token if refresh_token else None,
                        )
                        if await api.validate_token():
                            await api.close()
                            # Update config entry with new tokens
                            new_data = {**self.config_entry.data}
                            new_data[CONF_SMARTTHINGS_ACCESS_TOKEN] = access_token
                            new_data[CONF_SMARTTHINGS_REFRESH_TOKEN] = (
                                refresh_token if refresh_token else ""
                            )
                            new_data[CONF_SMARTTHINGS_TOKEN] = access_token
                            new_data[CONF_SMARTTHINGS_TOKEN_EXPIRES] = (
                                time.time() + 86400
                            )
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
            current_access_token = self.config_entry.data.get(
                CONF_SMARTTHINGS_ACCESS_TOKEN, ""
            )
            current_refresh_token = self.config_entry.data.get(
                CONF_SMARTTHINGS_REFRESH_TOKEN, ""
            )
            
            # Show masked tokens for security
            masked_access = (
                f"{'*' * (len(current_access_token) - 8)}{current_access_token[-8:]}"
                if len(current_access_token) > 8
                else "***"
            )
            masked_refresh = (
                f"{'*' * (len(current_refresh_token) - 8)}{current_refresh_token[-8:]}"
                if len(current_refresh_token) > 8
                else "(not set)"
            )

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_SMARTTHINGS_ACCESS_TOKEN,
                            description={"suggested_value": masked_access},
                        ): str,
                        vol.Optional(
                            CONF_SMARTTHINGS_REFRESH_TOKEN,
                            description={"suggested_value": masked_refresh},
                        ): str,
                    }
                ),
                errors=errors,
                description_placeholders={
                    "current_method": "SmartThings API with OAuth",
                    "info": "Update your OAuth tokens:\n"
                    "- Access Token: Your current token\n"
                    "- Refresh Token: Required for automatic renewal!\n\n"
                    f"Current Access Token: {masked_access}\n"
                    f"Current Refresh Token: {masked_refresh}",
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
                    "info": "Update IP address or PSK. No token expiration - permanent connection.",
                },
            )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidToken(HomeAssistantError):
    """Error to indicate invalid token."""

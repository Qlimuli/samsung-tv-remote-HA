"""Config flow for Samsung Remote integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
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
    CONF_SMARTTHINGS_TOKEN,
    CONF_TIMEOUT,
    DEFAULT_API_METHOD,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Remote."""

    VERSION = 1

    def __init__(self):
        """Initialize config flow."""
        self.api_method = DEFAULT_API_METHOD
        self.smartthings_api: Optional[SmartThingsAPI] = None
        self.devices: list[Dict[str, Any]] = []

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

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
        )

    async def async_step_smartthings(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle SmartThings API setup."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                token = user_input[CONF_SMARTTHINGS_TOKEN]
                self.smartthings_api = SmartThingsAPI(self.hass, token)

                # Validate token
                if not await self.smartthings_api.validate_token():
                    errors["base"] = "invalid_token"
                else:
                    # Fetch devices
                    self.devices = await self.smartthings_api.get_devices()
                    if not self.devices:
                        errors["base"] = "no_devices_found"
                    else:
                        return await self.async_step_select_device()
            except Exception as e:
                _LOGGER.error(f"SmartThings validation error: {e}")
                errors["base"] = "connection_error"

        return self.async_show_form(
            step_id="smartthings",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SMARTTHINGS_TOKEN): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "token_help": "Visit https://account.smartthings.com/tokens to generate"
            },
        )

    async def async_step_tizen_local(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle local Tizen setup."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                ip = user_input[CONF_LOCAL_IP]
                psk = user_input.get(CONF_LOCAL_PSK, "")
                
                api = TizenLocalAPI(ip, psk)
                if not await api.validate_connection():
                    errors["base"] = "connection_failed"
                else:
                    device_name = user_input.get(CONF_DEVICE_NAME, f"Samsung TV {ip}")
                    await self._async_create_entry(
                        device_name=device_name,
                        device_id=ip,
                        api_method="tizen_local",
                        local_ip=ip,
                        local_psk=psk,
                    )
            except Exception as e:
                _LOGGER.error(f"Tizen validation error: {e}")
                errors["base"] = "connection_error"

        return self.async_show_form(
            step_id="tizen_local",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOCAL_IP): str,
                    vol.Optional(CONF_LOCAL_PSK): str,
                    vol.Optional(CONF_DEVICE_NAME, default="Samsung TV"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_device(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle device selection."""
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device = next((d for d in self.devices if d["deviceId"] == device_id), None)
            
            if device:
                return await self._async_create_entry(
                    device_name=device.get("label", device_id),
                    device_id=device_id,
                    api_method="smartthings",
                    smartthings_token=self.smartthings_api.token,
                )

        device_options = {d["deviceId"]: d.get("label", d["deviceId"]) for d in self.devices}

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE_ID): vol.In(device_options)}
            ),
        )

    async def _async_create_entry(self, **kwargs: Any) -> FlowResult:
        """Create config entry."""
        await self.async_set_unique_id(kwargs[CONF_DEVICE_ID])
        self._abort_if_unique_id_configured()
        
        return self.async_create_entry(
            title=kwargs[CONF_DEVICE_NAME],
            data={
                CONF_DEVICE_ID: kwargs[CONF_DEVICE_ID],
                CONF_DEVICE_NAME: kwargs[CONF_DEVICE_NAME],
                CONF_API_METHOD: kwargs[CONF_API_METHOD],
                CONF_SMARTTHINGS_TOKEN: kwargs.get(CONF_SMARTTHINGS_TOKEN),
                CONF_LOCAL_IP: kwargs.get(CONF_LOCAL_IP),
                CONF_LOCAL_PSK: kwargs.get(CONF_LOCAL_PSK),
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
    pass


class InvalidToken(HomeAssistantError):
    """Error to indicate invalid token."""
    pass

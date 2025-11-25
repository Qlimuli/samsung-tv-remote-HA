"""Config flow for Samsung Remote integration with full OAuth 2.0."""

import time
import secrets
from typing import Any, Optional
from urllib.parse import urlencode

import voluptuous as vol
from aiohttp import ClientConnectorDNSError

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_entry_oauth2_flow

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
    CONF_SMARTTHINGS_CLIENT_ID,
    CONF_SMARTTHINGS_CLIENT_SECRET,
    DEFAULT_API_METHOD,
    DOMAIN,
    LOGGER,
    SMARTTHINGS_OAUTH_AUTHORIZE_URL,
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
        self.smartthings_client_id: Optional[str] = None
        self.smartthings_client_secret: Optional[str] = None
        self.oauth_state: Optional[str] = None

    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.api_method = user_input[CONF_API_METHOD]

            if self.api_method == "smartthings":
                return await self.async_step_smartthings_method()
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

    async def async_step_smartthings_method(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Choose between OAuth or PAT."""
        errors: dict[str, str] = {}

        if user_input is not None:
            method = user_input["method"]
            
            if method == "oauth":
                return await self.async_step_smartthings_oauth_setup()
            else:
                return await self.async_step_smartthings_pat()

        return self.async_show_form(
            step_id="smartthings_method",
            data_schema=vol.Schema(
                {
                    vol.Required("method"): vol.In({
                        "oauth": "OAuth 2.0 (Recommended - Auto-refresh)",
                        "pat": "Personal Access Token (Legacy - Manual refresh)"
                    }),
                }
            ),
            errors=errors,
            description_placeholders={
                "info": "**OAuth 2.0** (Recommended):\n"
                "- Tokens refresh automatically\n"
                "- Never expires\n"
                "- Requires SmartThings App registration\n\n"
                "**Personal Access Token** (PAT):\n"
                "- Simple setup\n"
                "- New PATs expire after 24 hours\n"
                "- Old PATs (before Dec 2024) never expire\n"
                "- Must be renewed manually"
            },
        )

    async def async_step_smartthings_oauth_setup(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Setup OAuth credentials."""
        errors: dict[str, str] = {}
        
        # Get the correct redirect URI
        if self.hass.config.external_url:
            base_url = self.hass.config.external_url
        elif self.hass.config.internal_url:
            base_url = self.hass.config.internal_url
        else:
            # Fallback to local URL
            base_url = "http://homeassistant.local:8123"
        
        # Use Home Assistant's OAuth callback endpoint
        redirect_uri = f"{base_url}/auth/external/callback"

        if user_input is not None:
            self.smartthings_client_id = user_input["client_id"].strip()
            self.smartthings_client_secret = user_input["client_secret"].strip()
            
            if not self.smartthings_client_id or not self.smartthings_client_secret:
                errors["base"] = "missing_credentials"
            else:
                # Generate OAuth state for security
                self.oauth_state = secrets.token_urlsafe(32)
                
                auth_params = {
                    "client_id": self.smartthings_client_id,
                    "redirect_uri": redirect_uri,
                    "response_type": "code",
                    "scope": "r:devices:* x:devices:*",
                    "state": self.oauth_state,
                }
                
                auth_url = f"{SMARTTHINGS_OAUTH_AUTHORIZE_URL}?{urlencode(auth_params)}"
                
                LOGGER.info(f"OAuth Redirect URI: {redirect_uri}")
                LOGGER.info(f"OAuth Authorization URL: {auth_url}")
                
                return self.async_external_step(
                    step_id="smartthings_oauth_callback",
                    url=auth_url
                )

        return self.async_show_form(
            step_id="smartthings_oauth_setup",
            data_schema=vol.Schema(
                {
                    vol.Required("client_id"): str,
                    vol.Required("client_secret"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "redirect_uri": redirect_uri,
                "setup_instructions": 
                "# SmartThings OAuth Setup\n\n"
                "## ⚠️ WICHTIG: Deine Redirect URI\n\n"
                f"Kopiere diese URI EXAKT in SmartThings:\n"
                f"```\n{redirect_uri}\n```\n\n"
                "## Schritt 1: SmartThings Developer Account\n\n"
                "1. Gehe zu: https://smartthings.developer.samsung.com/workspace/projects\n"
                "2. Klicke **'New Project'**\n"
                "3. Project Name: `Home Assistant`\n"
                "4. Project Type: **Automation**\n"
                "5. Klicke **'Create Project'**\n\n"
                "## Schritt 2: App registrieren\n\n"
                "1. Klicke **'Register App'**\n"
                "2. App Type: **Webhook Endpoint**\n"
                "3. App Name: `Home Assistant Samsung Remote`\n"
                "4. Target URL: `https://your-ha-url/api/webhook/smartthings` (beliebig)\n"
                "5. Scopes: ☑️ `r:devices:*` und ☑️ `x:devices:*`\n"
                "6. Klicke **'Register App'**\n\n"
                "## Schritt 3: OAuth Client erstellen\n\n"
                "1. Gehe zum Tab **'OAuth Settings'**\n"
                "2. Klicke **'Add OAuth Client'**\n"
                "3. **Redirect URI**: Kopiere die URI oben EXAKT!\n"
                f"   ```\n   {redirect_uri}\n   ```\n"
                "4. Klicke **'Generate OAuth Client'**\n"
                "5. Kopiere **Client ID** und **Client Secret**\n"
                "6. ⚠️ Client Secret wird nur EINMAL angezeigt!\n\n"
                "## Schritt 4: Hier eintragen\n\n"
                "Trage Client ID und Client Secret unten ein.\n\n"
                f"**Deine Redirect URI nochmal**: `{redirect_uri}`"
            },
        )

    async def async_step_smartthings_oauth_callback(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle OAuth callback."""
        errors: dict[str, str] = {}
        
        # Calculate redirect URI (same as in oauth_setup)
        if self.hass.config.external_url:
            base_url = self.hass.config.external_url
        elif self.hass.config.internal_url:
            base_url = self.hass.config.internal_url
        else:
            base_url = "http://homeassistant.local:8123"
        
        redirect_uri = f"{base_url}/auth/external/callback"
        
        if user_input is not None:
            code = user_input.get("code")
            state = user_input.get("state")
            error = user_input.get("error")
            
            if error:
                LOGGER.error(f"OAuth error from SmartThings: {error}")
                if error == "redirect_uri_mismatch":
                    return self.async_abort(
                        reason="redirect_uri_mismatch",
                        description_placeholders={
                            "redirect_uri": redirect_uri,
                            "error_detail": 
                                f"Die Redirect URI in SmartThings stimmt nicht überein!\n\n"
                                f"Erwartet wird EXAKT:\n{redirect_uri}\n\n"
                                f"Bitte prüfe in SmartThings Developer Console unter 'OAuth Settings'."
                        }
                    )
                return self.async_abort(reason=f"oauth_error_{error}")
            
            # Verify state to prevent CSRF
            if state != self.oauth_state:
                errors["base"] = "invalid_state"
                LOGGER.error("OAuth state mismatch - possible CSRF attack")
                return self.async_abort(reason="invalid_state")
            
            if not code:
                errors["base"] = "no_code"
                LOGGER.error("No authorization code received from SmartThings")
                return self.async_abort(reason="no_code")
            
            try:
                # Exchange authorization code for tokens
                api = SmartThingsAPI(
                    self.hass,
                    client_id=self.smartthings_client_id,
                    client_secret=self.smartthings_client_secret,
                )
                
                LOGGER.info(f"Exchanging code for tokens with redirect_uri: {redirect_uri}")
                
                tokens = await api.exchange_code_for_tokens(code, redirect_uri)
                
                self.smartthings_access_token = tokens["access_token"]
                self.smartthings_refresh_token = tokens["refresh_token"]
                self.smartthings_token_expires = time.time() + tokens.get("expires_in", 86400)
                
                LOGGER.info("Successfully obtained OAuth tokens from SmartThings")
                
                # Now fetch devices
                self.smartthings_api = SmartThingsAPI(
                    self.hass,
                    access_token=self.smartthings_access_token,
                    refresh_token=self.smartthings_refresh_token,
                    token_expires=self.smartthings_token_expires,
                    client_id=self.smartthings_client_id,
                    client_secret=self.smartthings_client_secret,
                )
                
                self.devices = await self.smartthings_api.get_devices()
                
                if not self.devices:
                    return self.async_abort(reason="no_devices_found")
                
                await self.smartthings_api.close()
                return await self.async_step_select_device()
                
            except Exception as e:
                LOGGER.error(f"OAuth token exchange failed: {e}", exc_info=True)
                errors["base"] = "token_exchange_failed"
                return self.async_abort(
                    reason="token_exchange_failed",
                    description_placeholders={
                        "error": str(e),
                        "redirect_uri": redirect_uri
                    }
                )

        return self.async_show_form(
            step_id="smartthings_oauth_callback",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    async def async_step_smartthings_pat(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle SmartThings PAT setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                access_token = user_input[CONF_SMARTTHINGS_ACCESS_TOKEN].strip()
                
                if not access_token:
                    errors["base"] = "invalid_token"
                    LOGGER.error("Access token is empty")
                    raise ValueError("Access token is required")

                if len(access_token) < 10:
                    errors["base"] = "invalid_token"
                    LOGGER.error(f"Access token too short (length: {len(access_token)})")
                    raise ValueError("Access token appears to be invalid (too short)")

                LOGGER.info(f"Validating SmartThings PAT token (length: {len(access_token)})")
                
                self.smartthings_api = SmartThingsAPI(
                    self.hass,
                    access_token=access_token,
                    refresh_token=None,  # PAT has no refresh token
                    token_expires=None,
                )

                LOGGER.info("Starting token validation...")
                if not await self.smartthings_api.validate_token():
                    errors["base"] = "invalid_token" 
                    LOGGER.error(f"Token validation failed for PAT token")
                else:
                    LOGGER.info("Token validation successful, fetching devices...")
                    try:
                        self.devices = await self.smartthings_api.get_devices()
                    except Exception as e:
                        LOGGER.warning(f"Could not fetch devices: {e}")
                        self.devices = []

                    if not self.devices:
                        errors["base"] = "no_devices_found"
                        LOGGER.error("No devices found in SmartThings account")
                    else:
                        self.smartthings_access_token = access_token
                        self.smartthings_refresh_token = None
                        self.smartthings_token_expires = None
                            
                        LOGGER.info(f"SmartThings PAT setup successful. Found {len(self.devices)} devices")

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

        return self.async_show_form(
            step_id="smartthings_pat",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SMARTTHINGS_ACCESS_TOKEN): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "token_help": "# Personal Access Token (PAT) Setup\n\n"
                "## Option 1: Old PAT (Created before Dec 2024)\n"
                "✅ **Never expires** - Use this if you have one!\n\n"
                "## Option 2: New PAT (Created after Dec 2024)\n"
                "⚠️ **Expires after 24 hours** - Must be renewed manually\n\n"
                "## How to get a PAT:\n\n"
                "1. Go to: https://account.smartthings.com/tokens\n"
                "2. Click **'Generate new token'**\n"
                "3. Select these scopes:\n"
                "   - ☑ `r:devices:*` (Read devices)\n"
                "   - ☑ `x:devices:*` (Execute devices)\n"
                "4. Click **'Generate token'**\n"
                "5. Copy the token and paste below\n\n"
                "⚠️ **Token Expiration**:\n"
                "- Old PATs: Never expire\n"
                "- New PATs: Expire after 24 hours\n"
                "- **Recommendation**: Use OAuth 2.0 instead for auto-refresh!\n\n"
                "📖 Full guide: https://github.com/Qlimuli/samsung-tv-remote-HA/blob/main/docs/SMARTTHINGS_SETUP.md"
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
                "ip_help": "# Local Tizen Setup\n\n"
                "✅ No token expiration\n"
                "✅ All commands supported\n"
                "✅ Faster response time\n\n"
                "Enter the IP address of your Samsung TV.\n\n"
                "**How to find your TV's IP:**\n"
                "1. TV Settings → Network → Network Status\n"
                "2. Or check your router's DHCP list\n\n"
                "**Pre-Shared Key (Optional)**:\n"
                "Only needed if you've enabled it on your TV"
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
                    smartthings_client_id=self.smartthings_client_id,
                    smartthings_client_secret=self.smartthings_client_secret,
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
            entry_data[CONF_SMARTTHINGS_CLIENT_ID] = kwargs.get(
                CONF_SMARTTHINGS_CLIENT_ID
            )
            entry_data[CONF_SMARTTHINGS_CLIENT_SECRET] = kwargs.get(
                CONF_SMARTTHINGS_CLIENT_SECRET
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
            if api_method == "smartthings":
                access_token = user_input.get(CONF_SMARTTHINGS_ACCESS_TOKEN, "").strip()

                if access_token:
                    try:
                        api = SmartThingsAPI(
                            self.hass,
                            access_token=access_token,
                            refresh_token=None,
                        )
                        if await api.validate_token():
                            await api.close()
                            new_data = {**self.config_entry.data}
                            new_data[CONF_SMARTTHINGS_ACCESS_TOKEN] = access_token
                            new_data[CONF_SMARTTHINGS_TOKEN] = access_token
                            # Don't update refresh token or client credentials
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
            
            masked_access = (
                f"{'*' * (len(current_access_token) - 8)}{current_access_token[-8:]}"
                if len(current_access_token) > 8
                else "***"
            )

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_SMARTTHINGS_ACCESS_TOKEN,
                            description={"suggested_value": masked_access},
                        ): str,
                    }
                ),
                errors=errors,
                description_placeholders={
                    "current_method": "SmartThings API",
                    "info": f"Current Access Token: {masked_access}\n\n"
                    "⚠️ **Important**:\n"
                    "- OAuth tokens refresh automatically - no need to update\n"
                    "- PAT tokens expire after 24 hours (if created after Dec 2024)\n"
                    "- Only update if you want to switch to a different token\n\n"
                    "💡 **Tip**: If using PAT and it expires daily, consider setting up OAuth 2.0 instead!",
                },
            )
        else:
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

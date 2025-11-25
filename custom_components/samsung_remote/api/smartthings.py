"""SmartThings API client with full OAuth 2.0 support."""

import asyncio
import time
from typing import Any, Optional

import aiohttp
from aiohttp import ClientConnectorDNSError
from homeassistant.core import HomeAssistant

from ..const import (
    DEFAULT_TIMEOUT,
    LOGGER,
    SAMSUNG_KEY_MAP,
    SMARTTHINGS_COMMANDS,
    SMARTTHINGS_OAUTH_TOKEN_URL,
    CONF_SMARTTHINGS_ACCESS_TOKEN,
    CONF_SMARTTHINGS_REFRESH_TOKEN,
    CONF_SMARTTHINGS_TOKEN_EXPIRES,
    CONF_SMARTTHINGS_CLIENT_ID,
    CONF_SMARTTHINGS_CLIENT_SECRET,
)


class SmartThingsAPI:
    """SmartThings API client with full OAuth 2.0 token management."""

    def __init__(
        self,
        hass: HomeAssistant,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires: Optional[float] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize SmartThings client."""
        self.hass = hass
        self.access_token = access_token.strip() if access_token else None
        self.refresh_token = refresh_token.strip() if refresh_token else None
        self.token_expires = token_expires
        self.client_id = client_id.strip() if client_id else None
        self.client_secret = client_secret.strip() if client_secret else None
        self.timeout = timeout
        self.base_url = "https://api.smartthings.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.device_cache: dict[str, dict[str, Any]] = {}
        self.device_capabilities: dict[str, list[str]] = {}
        self._command_lock = asyncio.Lock()
        self._last_command_time = 0.0
        self._token_refresh_lock = asyncio.Lock()
        
        # Determine token type
        self._is_pat_token = not self.refresh_token
        self._is_oauth_token = bool(self.refresh_token and self.client_id and self.client_secret)
        
        if self._is_oauth_token:
            LOGGER.info("Initialized with OAuth 2.0 (auto-refresh enabled)")
        elif self._is_pat_token:
            LOGGER.info("Initialized with PAT token (no auto-refresh)")
        else:
            LOGGER.warning("Initialized with refresh token but missing client credentials - refresh will fail!")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        if not self.client_id or not self.client_secret:
            raise Exception("Client ID and Client Secret required for OAuth")

        try:
            session = await self._get_session()
            
            payload = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            LOGGER.info(f"Exchanging authorization code for tokens...")
            
            async with session.post(
                SMARTTHINGS_OAUTH_TOKEN_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status == 200:
                    tokens = await resp.json()
                    LOGGER.info("Successfully obtained OAuth tokens")
                    return tokens
                else:
                    error_text = await resp.text()
                    LOGGER.error(f"Token exchange failed ({resp.status}): {error_text}")
                    raise Exception(f"Token exchange failed: {error_text}")
        except Exception as e:
            LOGGER.error(f"Error exchanging code for tokens: {e}")
            raise

    async def _refresh_token_if_needed(self) -> bool:
        """Refresh OAuth token if it's about to expire."""
        # PAT tokens cannot be refreshed
        if self._is_pat_token:
            LOGGER.debug("Using PAT token - no refresh possible")
            return True

        # Check if we have OAuth credentials
        if not self._is_oauth_token:
            LOGGER.warning("Cannot refresh: missing client_id or client_secret")
            return False

        async with self._token_refresh_lock:
            # Check if token needs refresh
            if self.token_expires:
                time_until_expiry = self.token_expires - time.time()
                if time_until_expiry > 300:  # 5 minutes buffer
                    LOGGER.debug(f"Token valid for {time_until_expiry:.0f}s, no refresh needed")
                    return True

            try:
                LOGGER.info("Refreshing OAuth token...")
                session = await self._get_session()

                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }

                async with session.post(
                    SMARTTHINGS_OAUTH_TOKEN_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as resp:
                    if resp.status == 200:
                        response_data = await resp.json()
                        old_token = self.access_token[:20] if self.access_token else "unknown"
                        
                        self.access_token = response_data["access_token"]
                        
                        # Refresh token might rotate
                        if "refresh_token" in response_data:
                            self.refresh_token = response_data["refresh_token"]
                            LOGGER.debug("Refresh token was rotated")
                        
                        expires_in = response_data.get("expires_in", 86400)
                        self.token_expires = time.time() + expires_in
                        
                        new_token = self.access_token[:20]
                        LOGGER.info(f"✅ Token refreshed successfully: {old_token}... → {new_token}... (valid for {expires_in}s)")

                        # Update config entry with new tokens
                        for entry in self.hass.config_entries.async_entries("samsung_remote"):
                            if entry.entry_id and entry.data.get(CONF_SMARTTHINGS_ACCESS_TOKEN):
                                new_data = {**entry.data}
                                new_data[CONF_SMARTTHINGS_ACCESS_TOKEN] = self.access_token
                                new_data[CONF_SMARTTHINGS_REFRESH_TOKEN] = self.refresh_token
                                new_data[CONF_SMARTTHINGS_TOKEN_EXPIRES] = self.token_expires
                                self.hass.config_entries.async_update_entry(entry, data=new_data)
                                LOGGER.debug("Config entry updated with new tokens")

                        return True
                    else:
                        error_text = await resp.text()
                        LOGGER.error(
                            f"❌ Token refresh failed ({resp.status}): {error_text}\n\n"
                            f"Possible causes:\n"
                            f"1. Refresh token expired or revoked\n"
                            f"2. Invalid client credentials\n"
                            f"3. SmartThings API temporarily unavailable\n\n"
                            f"Action needed: Update OAuth credentials in integration settings"
                        )
                        return False
                        
            except asyncio.TimeoutError:
                LOGGER.error("Token refresh timeout - network issue")
                return False
            except Exception as e:
                LOGGER.error(f"Token refresh error: {e}")
                return False

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make API request with automatic token refresh."""
        # Try to refresh token before request if needed
        if retry_count == 0 and self._is_oauth_token:
            if self.token_expires:
                time_until_expiry = self.token_expires - time.time()
                if time_until_expiry < 300:  # Less than 5 minutes
                    refresh_success = await self._refresh_token_if_needed()
                    if not refresh_success:
                        LOGGER.warning("Token refresh failed, attempting request anyway...")

        if not self.access_token:
            raise Exception("Access token is not set")

        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token.strip()}",
            "Content-Type": "application/json",
        }

        try:
            async with session.request(
                method,
                url,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status in (200, 201):
                    return await resp.json()
                elif resp.status == 401:
                    error_text = await resp.text()
                    
                    # Try to refresh token and retry once
                    if retry_count == 0 and self._is_oauth_token:
                        LOGGER.warning("401 Unauthorized - attempting token refresh...")
                        if await self._refresh_token_if_needed():
                            LOGGER.info("Token refreshed, retrying request...")
                            return await self._request(method, endpoint, data, retry_count + 1, max_retries)
                    
                    LOGGER.error(
                        f"❌ Authentication failed (401):\n"
                        f"Your access token is invalid or expired.\n\n"
                        f"{'OAuth: Automatic refresh failed. ' if self._is_oauth_token else 'PAT: '}"
                        f"Please update your credentials in:\n"
                        f"Settings → Devices & Services → Samsung Remote → Options\n\n"
                        f"Response: {error_text[:200]}"
                    )
                    raise Exception(f"Authentication failed (401): {error_text[:200]}")
                    
                elif resp.status == 403:
                    error_text = await resp.text()
                    LOGGER.error(
                        f"❌ Permission denied (403):\n"
                        f"Your token lacks required scopes.\n\n"
                        f"Required scopes:\n"
                        f"- r:devices:* (Read devices)\n"
                        f"- x:devices:* (Execute devices)\n\n"
                        f"Response: {error_text[:200]}"
                    )
                    raise Exception(f"Permission denied (403): {error_text[:200]}")
                    
                elif resp.status == 429 and retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    LOGGER.warning(f"Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    return await self._request(method, endpoint, data, retry_count + 1, max_retries)
                    
                else:
                    error_text = await resp.text()
                    raise Exception(f"SmartThings API error {resp.status}: {error_text[:200]}")
                    
        except asyncio.TimeoutError:
            if retry_count < max_retries:
                LOGGER.warning("Request timeout, retrying...")
                await asyncio.sleep(2 ** retry_count)
                return await self._request(method, endpoint, data, retry_count + 1, max_retries)
            raise
        except Exception as e:
            LOGGER.error(f"Request failed: {e}")
            raise

    async def get_devices(self) -> list[dict[str, Any]]:
        """Fetch all TV devices from SmartThings."""
        try:
            response = await self._request("GET", "/devices")
            devices = response.get("items", [])
            
            tv_devices = []
            for device in devices:
                if self._is_tv_device(device):
                    device_id = device["deviceId"]
                    self.device_cache[device_id] = device
                    
                    capabilities = self._get_device_capabilities(device)
                    self.device_capabilities[device_id] = capabilities
                    LOGGER.info(f"Found TV: {device.get('label', device_id)}")
                    
                    tv_devices.append(device)
            
            LOGGER.info(f"Discovered {len(tv_devices)} TV device(s)")
            return tv_devices
        except Exception as e:
            LOGGER.error(f"Failed to fetch devices: {e}")
            raise

    def _get_device_capabilities(self, device: dict[str, Any]) -> list[str]:
        """Extract capabilities from device."""
        capabilities = []
        components = device.get("components", [])
        if components and isinstance(components, list):
            for component in components:
                caps = component.get("capabilities", [])
                for cap in caps:
                    if isinstance(cap, dict):
                        cap_id = cap.get("id", "")
                        if cap_id:
                            capabilities.append(cap_id)
        return capabilities

    def _is_tv_device(self, device: dict[str, Any]) -> bool:
        """Check if device is a TV."""
        device_type = device.get("deviceTypeName", "").lower()
        device_type_id = device.get("deviceType", "").lower()
        
        if "tv" in device_type or "tv" in device_type_id:
            return True
        
        capabilities = self._get_device_capabilities(device)
        tv_capabilities = [
            "samsungvd.remoteControl",
            "samsungvd.mediaInputSource",
            "samsungvd.ambientContent",
            "mediaPlayback",
            "tvChannel",
            "audioVolume"
        ]
        
        return any(cap in capabilities for cap in tv_capabilities)

    async def send_command(self, device_id: str, command: str) -> bool:
        """Send remote command to device."""
        async with self._command_lock:
            try:
                current_time = time.time()
                time_since_last = current_time - self._last_command_time
                min_delay = 0.3
                
                if time_since_last < min_delay:
                    delay_needed = min_delay - time_since_last
                    await asyncio.sleep(delay_needed)
                
                key = SAMSUNG_KEY_MAP.get(command, command)
                
                if key not in SMARTTHINGS_COMMANDS:
                    LOGGER.warning(
                        f"⚠️ Command '{command}' not supported by SmartThings API\n"
                        f"Supported: {', '.join(sorted(SMARTTHINGS_COMMANDS))}\n"
                        f"Use Tizen Local API for full command support"
                    )
                    return False
                
                payload = {
                    "commands": [
                        {
                            "component": "main",
                            "capability": "samsungvd.remoteControl",
                            "command": "send",
                            "arguments": [key]
                        }
                    ]
                }
                
                await self._request("POST", f"/devices/{device_id}/commands", payload)
                self._last_command_time = time.time()
                LOGGER.debug(f"✅ Command sent: {command} (key: {key})")
                return True
                
            except Exception as e:
                LOGGER.error(f"❌ Command failed: {command} - {e}")
                return False

    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        """Get device status."""
        try:
            response = await self._request("GET", f"/devices/{device_id}/status")
            return response
        except Exception as e:
            LOGGER.error(f"Failed to get device status: {e}")
            return {}

    async def validate_token(self) -> bool:
        """Validate SmartThings token."""
        try:
            if not self.access_token:
                LOGGER.error("No access token provided")
                return False
            
            LOGGER.info("Validating SmartThings token...")
            
            session = await self._get_session()
            url = f"{self.base_url}/devices"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    is_valid = "items" in response_data
                    if is_valid:
                        LOGGER.info("✅ Token validation successful")
                    else:
                        LOGGER.error("❌ Token validation failed: Invalid response")
                    return is_valid
                elif resp.status == 401:
                    error_text = await resp.text()
                    LOGGER.error(f"❌ Token validation failed (401): Token is invalid or expired")
                    return False
                elif resp.status == 403:
                    error_text = await resp.text()
                    LOGGER.error(f"❌ Token validation failed (403): Token lacks permissions")
                    return False
                else:
                    error_text = await resp.text()
                    LOGGER.error(f"❌ Token validation failed ({resp.status}): {error_text[:200]}")
                    return False

        except ClientConnectorDNSError as e:
            LOGGER.warning(f"Network/DNS error during validation: {e}. Allowing startup...")
            return True
        except asyncio.TimeoutError:
            LOGGER.warning("Token validation timeout. Allowing startup...")
            return True
        except Exception as e:
            LOGGER.error(f"Token validation error: {e}", exc_info=True)
            return False

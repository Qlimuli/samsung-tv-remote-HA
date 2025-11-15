"""Services for Samsung Remote integration."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceNotFound

from .const import CONF_API_METHOD, DOMAIN
from .api.smartthings import SmartThingsAPI

LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Samsung Remote."""

    async def refresh_token_service(call: ServiceCall) -> None:
        """Manually refresh SmartThings OAuth token."""
        entry_id = call.data.get("entry_id")
        
        if not entry_id:
            LOGGER.error("entry_id is required for token refresh")
            return
        
        if DOMAIN not in hass.data or entry_id not in hass.data[DOMAIN]:
            LOGGER.error(f"Entry {entry_id} not found")
            return
        
        api = hass.data[DOMAIN][entry_id].get("api")
        
        if not isinstance(api, SmartThingsAPI):
            LOGGER.error("This service only works with SmartThings API")
            return
        
        try:
            if await api._refresh_token_if_needed():
                LOGGER.info("SmartThings token refreshed successfully")
            else:
                LOGGER.error("Failed to refresh SmartThings token - check your refresh token configuration")
        except Exception as e:
            LOGGER.error(f"Error refreshing token: {e}")

    hass.services.async_register(
        DOMAIN,
        "refresh_oauth_token",
        refresh_token_service,
        description="Manually refresh SmartThings OAuth token",
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services."""
    hass.services.async_remove(DOMAIN, "refresh_oauth_token")

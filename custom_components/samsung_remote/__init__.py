"""Samsung Remote integration."""

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_entry_oauth2_flow

from .api.smartthings import SmartThingsAPI
from .api.tizen_local import TizenLocalAPI
from .const import (
    CONF_API_METHOD,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_LOCAL_IP,
    CONF_LOCAL_PSK,
    DOMAIN,
    LOGGER,
)

PLATFORMS: Final = ["remote", "button"]


async def get_smartthings_token(hass: HomeAssistant) -> str | None:
    """Get SmartThings API token from existing SmartThings integration."""
    if "smartthings" not in hass.data:
        LOGGER.debug("SmartThings integration not found in hass.data")
        return None
    
    # Try to get token from SmartThings integration entries
    for entry in hass.config_entries.async_entries("smartthings"):
        LOGGER.debug(f"Checking SmartThings entry: {entry.entry_id}")
        
        # Check if entry has data with access_token
        if entry.data.get("access_token"):
            LOGGER.info("Found access_token in SmartThings entry data")
            return entry.data["access_token"]
        
        # Check if entry uses OAuth2 implementation
        if entry.data.get("auth_implementation"):
            try:
                # Get OAuth2 session from implementation
                implementation = await config_entry_oauth2_flow.async_get_config_entry_implementation(
                    hass, entry
                )
                if implementation:
                    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
                    token_data = await session.async_ensure_token_valid()
                    if token_data and "access_token" in token_data:
                        LOGGER.info("Retrieved access_token from OAuth2 session")
                        return token_data["access_token"]
            except Exception as e:
                LOGGER.warning(f"Could not retrieve OAuth2 token: {e}")
        
        # Check runtime_data if available (Home Assistant 2024.x+)
        if hasattr(entry, "runtime_data") and entry.runtime_data:
            if hasattr(entry.runtime_data, "token"):
                LOGGER.info("Found token in entry.runtime_data")
                return entry.runtime_data.token
    
    LOGGER.warning("No valid SmartThings token found in any entry")
    return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Samsung Remote from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    try:
        api_method = entry.data.get(CONF_API_METHOD, "smartthings")

        if api_method == "smartthings":
            # Always try to use existing SmartThings integration
            token = await get_smartthings_token(hass)
            
            if not token:
                raise ConfigEntryNotReady(
                    "SmartThings integration not found or not configured. "
                    "Please set up the native SmartThings integration first via "
                    "Settings > Devices & Services > Add Integration > SmartThings"
                )
            
            LOGGER.info("Using token from existing SmartThings integration")
            api = SmartThingsAPI(hass, token=token)

            # Validate token
            if not await api.validate_token():
                LOGGER.error("SmartThings token validation failed. Please reconfigure SmartThings integration.")
                raise ConfigEntryNotReady(
                    "SmartThings token invalid. Please reconfigure the SmartThings integration."
                )
        else:
            # Tizen Local API
            ip = entry.data.get(CONF_LOCAL_IP)
            if not ip:
                raise ConfigEntryNotReady("Local IP missing")

            psk = entry.data.get(CONF_LOCAL_PSK, "")
            api = TizenLocalAPI(ip, psk)

            # Validate connection
            if not await api.validate_connection():
                raise ConfigEntryNotReady(f"Cannot reach TV at {ip}")

        hass.data[DOMAIN][entry.entry_id] = {
            "api": api,
            "device_id": entry.data.get(CONF_DEVICE_ID),
            "device_name": entry.data.get(CONF_DEVICE_NAME),
        }

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

        return True

    except ConfigEntryNotReady:
        raise
    except Exception as e:
        LOGGER.error(f"Error setting up Samsung Remote: {e}", exc_info=True)
        raise ConfigEntryNotReady(str(e))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        api = hass.data[DOMAIN][entry.entry_id].get("api")
        if api and hasattr(api, "close"):
            await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

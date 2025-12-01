"""Samsung Remote integration."""

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

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
    
    # Check if smartthings integration is loaded
    smartthings_entries = hass.config_entries.async_entries("smartthings")
    
    if not smartthings_entries:
        LOGGER.warning("No SmartThings integration entries found")
        return None
    
    LOGGER.info(f"Found {len(smartthings_entries)} SmartThings entries")
    
    for entry in smartthings_entries:
        LOGGER.debug(f"Checking SmartThings entry: {entry.entry_id}, state: {entry.state}")
        
        # Skip entries that are not loaded
        if entry.state.name != "LOADED":
            LOGGER.debug(f"Skipping entry {entry.entry_id} - state is {entry.state.name}")
            continue
        
        # Method 1: Check entry.data for access_token
        if "access_token" in entry.data:
            token = entry.data["access_token"]
            # Token might be a dict with 'access_token' key
            if isinstance(token, dict):
                if "access_token" in token:
                    token = token["access_token"]
                    LOGGER.info(f"Found access_token in dict (length: {len(token)})")
                    return token
            elif isinstance(token, str):
                LOGGER.info(f"Found access_token string in entry.data (length: {len(token)})")
                return token
        
        # Method 2: Check entry.data for token
        if "token" in entry.data:
            token = entry.data["token"]
            # Token might be a dict with 'access_token' key
            if isinstance(token, dict):
                if "access_token" in token:
                    token = token["access_token"]
                    LOGGER.info(f"Found access_token in token dict (length: {len(token)})")
                    return token
            elif isinstance(token, str):
                LOGGER.info(f"Found token string in entry.data (length: {len(token)})")
                return token
        
        # Method 3: Check runtime_data if available (HA 2024.x+)
        if hasattr(entry, "runtime_data") and entry.runtime_data:
            LOGGER.debug("Entry has runtime_data")
            
            # Check for token attribute
            if hasattr(entry.runtime_data, "token"):
                token = entry.runtime_data.token
                # Token might be a dict
                if isinstance(token, dict) and "access_token" in token:
                    token = token["access_token"]
                if isinstance(token, str):
                    LOGGER.info(f"Found token in runtime_data.token (length: {len(token)})")
                    return token
            
            # Check for access_token attribute
            if hasattr(entry.runtime_data, "access_token"):
                token = entry.runtime_data.access_token
                # Token might be a dict
                if isinstance(token, dict) and "access_token" in token:
                    token = token["access_token"]
                if isinstance(token, str):
                    LOGGER.info(f"Found token in runtime_data.access_token (length: {len(token)})")
                    return token
            
            # If runtime_data is a dict
            if isinstance(entry.runtime_data, dict):
                if "token" in entry.runtime_data:
                    token = entry.runtime_data["token"]
                    # Token might be a dict
                    if isinstance(token, dict) and "access_token" in token:
                        token = token["access_token"]
                    if isinstance(token, str):
                        LOGGER.info(f"Found token in runtime_data dict (length: {len(token)})")
                        return token
                if "access_token" in entry.runtime_data:
                    token = entry.runtime_data["access_token"]
                    # Token might be a dict
                    if isinstance(token, dict) and "access_token" in token:
                        token = token["access_token"]
                    if isinstance(token, str):
                        LOGGER.info(f"Found access_token in runtime_data dict (length: {len(token)})")
                        return token
        
        # Method 4: Try to get from hass.data
        if "smartthings" in hass.data and entry.entry_id in hass.data["smartthings"]:
            smartthings_data = hass.data["smartthings"][entry.entry_id]
            LOGGER.debug(f"Found smartthings data in hass.data, type: {type(smartthings_data)}")
            
            # Check if it's a SmartThings API instance with token
            if hasattr(smartthings_data, "token"):
                token = smartthings_data.token
                # Token might be a dict
                if isinstance(token, dict) and "access_token" in token:
                    token = token["access_token"]
                if isinstance(token, str):
                    LOGGER.info(f"Found token in hass.data smartthings object (length: {len(token)})")
                    return token
            
            # Check if it's a dict
            if isinstance(smartthings_data, dict):
                if "token" in smartthings_data:
                    token = smartthings_data["token"]
                    # Token might be a dict
                    if isinstance(token, dict) and "access_token" in token:
                        token = token["access_token"]
                    if isinstance(token, str):
                        LOGGER.info(f"Found token in hass.data dict (length: {len(token)})")
                        return token
                if "access_token" in smartthings_data:
                    token = smartthings_data["access_token"]
                    # Token might be a dict
                    if isinstance(token, dict) and "access_token" in token:
                        token = token["access_token"]
                    if isinstance(token, str):
                        LOGGER.info(f"Found access_token in hass.data dict (length: {len(token)})")
                        return token
        
        LOGGER.debug(f"Entry {entry.entry_id} checked, no token found in any location")
    
    LOGGER.error("No valid SmartThings token found in any entry after checking all methods")
    return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Samsung Remote from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    try:
        api_method = entry.data.get(CONF_API_METHOD, "smartthings")
        LOGGER.info(f"Setting up Samsung Remote with method: {api_method}")

        if api_method == "smartthings":
            # Always try to use existing SmartThings integration
            LOGGER.info("Attempting to get token from SmartThings integration...")
            token = await get_smartthings_token(hass)
            
            if not token:
                error_msg = (
                    "SmartThings integration not found or not configured.\n\n"
                    "Please set up the native SmartThings integration first:\n"
                    "1. Go to Settings > Devices & Services\n"
                    "2. Click 'Add Integration'\n"
                    "3. Search for 'SmartThings'\n"
                    "4. Complete the setup\n"
                    "5. Then try adding Samsung Remote again"
                )
                LOGGER.error(error_msg)
                raise ConfigEntryNotReady(error_msg)
            
            LOGGER.info(f"Successfully obtained SmartThings token (length: {len(token)})")
            api = SmartThingsAPI(hass, token=token)

            # Validate token
            LOGGER.info("Validating SmartThings token...")
            if not await api.validate_token():
                LOGGER.error("SmartThings token validation failed")
                raise ConfigEntryNotReady(
                    "SmartThings token is invalid. Please reconfigure the SmartThings integration."
                )
            
            LOGGER.info("SmartThings token validated successfully")
        else:
            # Tizen Local API
            ip = entry.data.get(CONF_LOCAL_IP)
            if not ip:
                raise ConfigEntryNotReady("Local IP missing")

            psk = entry.data.get(CONF_LOCAL_PSK, "")
            LOGGER.info(f"Setting up Tizen Local API for {ip}")
            api = TizenLocalAPI(ip, psk)

            # Validate connection
            if not await api.validate_connection():
                raise ConfigEntryNotReady(f"Cannot reach TV at {ip}")

        hass.data[DOMAIN][entry.entry_id] = {
            "api": api,
            "device_id": entry.data.get(CONF_DEVICE_ID),
            "device_name": entry.data.get(CONF_DEVICE_NAME),
        }

        LOGGER.info(f"Setting up platforms: {PLATFORMS}")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

        LOGGER.info("Samsung Remote setup completed successfully")
        return True

    except ConfigEntryNotReady:
        raise
    except Exception as e:
        LOGGER.error(f"Error setting up Samsung Remote: {e}", exc_info=True)
        raise ConfigEntryNotReady(str(e))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    LOGGER.info(f"Unloading Samsung Remote entry: {entry.entry_id}")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        api = hass.data[DOMAIN][entry.entry_id].get("api")
        if api and hasattr(api, "close"):
            await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    LOGGER.info(f"Reloading Samsung Remote entry: {entry.entry_id}")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

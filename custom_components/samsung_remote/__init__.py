"""Samsung Remote integration."""

import asyncio
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import async_migrate_entries

from .const import DOMAIN, LOGGER
from .api.smartthings import SmartThingsAPI
from .api.tizen_local import TizenLocalAPI

PLATFORMS: Final = ["remote"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Samsung Remote from a config entry."""
    
    hass.data.setdefault(DOMAIN, {})
    
    try:
        api_method = entry.data.get("api_method", "smartthings")
        
        if api_method == "smartthings":
            token = entry.data.get("smartthings_token")
            api = SmartThingsAPI(hass, token)
            
            # Validate token
            if not await api.validate_token():
                raise ConfigEntryNotReady("Invalid SmartThings token")
        else:
            ip = entry.data.get("local_ip")
            psk = entry.data.get("local_psk", "")
            api = TizenLocalAPI(ip, psk)
            
            # Validate connection
            if not await api.validate_connection():
                raise ConfigEntryNotReady(f"Cannot reach TV at {ip}")
        
        hass.data[DOMAIN][entry.entry_id] = {
            "api": api,
            "device_id": entry.data.get("device_id"),
            "device_name": entry.data.get("device_name"),
        }
        
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))
        
        return True
        
    except Exception as e:
        LOGGER.error(f"Error setting up Samsung Remote: {e}")
        raise ConfigEntryNotReady(str(e))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data:
        api = hass.data[DOMAIN][entry.entry_id].get("api")
        if api:
            await api.close()
        del hass.data[DOMAIN][entry.entry_id]
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

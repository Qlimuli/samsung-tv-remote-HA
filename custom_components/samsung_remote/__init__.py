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
    CONF_SMARTTHINGS_ACCESS_TOKEN,
    CONF_SMARTTHINGS_REFRESH_TOKEN,
    CONF_SMARTTHINGS_TOKEN,
    CONF_SMARTTHINGS_TOKEN_EXPIRES,
    DOMAIN,
    LOGGER,
)

PLATFORMS: Final = ["remote", "button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Samsung Remote from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    try:
        api_method = entry.data.get(CONF_API_METHOD, "smartthings")

        if api_method == "smartthings":
            access_token = entry.data.get(CONF_SMARTTHINGS_ACCESS_TOKEN)
            refresh_token = entry.data.get(CONF_SMARTTHINGS_REFRESH_TOKEN)
            token_expires = entry.data.get(CONF_SMARTTHINGS_TOKEN_EXPIRES)

            # Fallback to old PAT format if no OAuth tokens present
            if not access_token:
                access_token = entry.data.get(CONF_SMARTTHINGS_TOKEN)

            if not access_token:
                raise ConfigEntryNotReady("SmartThings token missing")

            api = SmartThingsAPI(
                hass,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires=token_expires,
            )

            # Validate token
            if not await api.validate_token():
                raise ConfigEntryNotReady("Invalid SmartThings token")
        else:
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

    except Exception as e:
        LOGGER.error(f"Error setting up Samsung Remote: {e}")
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

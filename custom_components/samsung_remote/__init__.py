"""Samsung Remote Integration for Home Assistant."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import config_entry_oauth2_flow

_LOGGER = logging.getLogger(__name__)

DOMAIN = "samsung_remote"
PLATFORMS = [Platform.REMOTE, Platform.BUTTON]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Samsung Remote from a config entry."""
    _LOGGER.debug("Setting up Samsung Remote integration")
    
    hass.data.setdefault(DOMAIN, {})
    
    # Prüfe die Verbindungsmethode
    connection_method = entry.data.get("connection_method", "smartthings")
    
    if connection_method == "smartthings":
        # Versuche das SmartThings Token aus der nativen Integration zu holen
        smartthings_token = await _get_smartthings_token_from_integration(hass)
        
        if not smartthings_token:
            _LOGGER.error(
                "SmartThings integration not found or not configured. "
                "Please set up the native SmartThings integration first:\n"
                "1. Go to Settings > Devices & Services\n"
                "2. Click 'Add Integration'\n"
                "3. Search for 'SmartThings'\n"
                "4. Complete the setup\n"
                "5. Then restart this integration"
            )
            return False
        
        # Speichere das Token in den Entry-Daten
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, "access_token": smartthings_token}
        )
        
        _LOGGER.info("Successfully retrieved SmartThings token from native integration")
    
    # Speichere die Entry-Daten
    hass.data[DOMAIN][entry.entry_id] = {
        "entry": entry,
        "connection_method": connection_method,
    }
    
    # Lade die Plattformen
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def _get_smartthings_token_from_integration(hass: HomeAssistant) -> str | None:
    """Hole das SmartThings Token aus der nativen Integration."""
    _LOGGER.debug("Attempting to retrieve SmartThings token from native integration")
    
    # Methode 1: Prüfe ob die SmartThings Integration geladen ist
    if "smartthings" in hass.data:
        _LOGGER.debug("SmartThings integration found in hass.data")
        
        # Versuche die Config Entries zu finden
        smartthings_entries = hass.config_entries.async_entries("smartthings")
        
        if smartthings_entries:
            _LOGGER.debug(f"Found {len(smartthings_entries)} SmartThings config entries")
            
            for st_entry in smartthings_entries:
                # Hole das Token aus dem OAuth2 Implementation
                try:
                    # Prüfe ob es eine OAuth2 Session gibt
                    if hasattr(st_entry, "data") and "token" in st_entry.data:
                        token_data = st_entry.data["token"]
                        access_token = token_data.get("access_token")
                        
                        if access_token:
                            _LOGGER.info("Successfully retrieved access token from SmartThings entry")
                            return access_token
                    
                    # Alternative: Nutze die OAuth2 Session direkt
                    implementation = await config_entry_oauth2_flow.async_get_implementation(
                        hass, "smartthings"
                    )
                    
                    if implementation:
                        session = config_entry_oauth2_flow.OAuth2Session(
                            hass, st_entry, implementation
                        )
                        
                        # Hole das Token
                        token = await session.async_ensure_token_valid()
                        
                        if token and "access_token" in token:
                            _LOGGER.info("Successfully retrieved access token via OAuth2 session")
                            return token["access_token"]
                            
                except Exception as e:
                    _LOGGER.debug(f"Failed to get token from entry {st_entry.entry_id}: {e}")
                    continue
    
    # Methode 2: Suche in allen Config Entries
    _LOGGER.debug("Searching all config entries for SmartThings")
    all_entries = hass.config_entries.async_entries()
    
    for entry in all_entries:
        if entry.domain == "smartthings":
            _LOGGER.debug(f"Found SmartThings entry: {entry.entry_id}")
            
            # Versuche Token aus verschiedenen Quellen
            if "token" in entry.data:
                token_data = entry.data["token"]
                if isinstance(token_data, dict) and "access_token" in token_data:
                    _LOGGER.info("Found access token in entry data")
                    return token_data["access_token"]
            
            # Prüfe auch die alten Token-Formate
            if "access_token" in entry.data:
                _LOGGER.info("Found direct access token in entry data")
                return entry.data["access_token"]
    
    _LOGGER.warning("No valid SmartThings token found in any method")
    return None


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Samsung Remote integration")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

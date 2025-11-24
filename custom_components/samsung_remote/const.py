"""Constants for Samsung Remote integration."""

import logging
from enum import Enum

DOMAIN = "samsung_remote"
LOGGER = logging.getLogger(__name__)

# Configuration
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_API_METHOD = "api_method"
CONF_SMARTTHINGS_TOKEN = "smartthings_token"
CONF_SMARTTHINGS_REFRESH_TOKEN = "smartthings_refresh_token"
CONF_SMARTTHINGS_ACCESS_TOKEN = "smartthings_access_token"
CONF_SMARTTHINGS_TOKEN_EXPIRES = "smartthings_token_expires"
CONF_LOCAL_IP = "local_ip"
CONF_LOCAL_PSK = "local_psk"
CONF_TIMEOUT = "timeout"

# OAuth Configuration
SMARTTHINGS_OAUTH_AUTHORIZE_URL = "https://api.smartthings.com/oauth/authorize"
SMARTTHINGS_OAUTH_TOKEN_URL = "https://api.smartthings.com/oauth/token"
SMARTTHINGS_OAUTH_SCOPES = ["r:devices:*", "x:devices:*"]

# Defaults
DEFAULT_TIMEOUT = 10
DEFAULT_API_METHOD = "smartthings"

# API Methods
class APIMethod(Enum):
    """API connection methods."""
    SMARTTHINGS = "smartthings"
    TIZEN_LOCAL = "tizen_local"


# SmartThings API supported commands (limited set)
# Only these commands work with SmartThings samsungvd.remoteControl capability
SMARTTHINGS_COMMANDS = {
    "UP", "DOWN", "LEFT", "RIGHT", "OK", "BACK", "EXIT", 
    "MENU", "HOME", "MUTE", "PLAY", "PAUSE", "STOP", 
    "REWIND", "FF", "PLAY_BACK", "SOURCE"
}

# Samsung TV Key Codes - Maps user-friendly names to API commands
# For SmartThings API: Only uses commands from SMARTTHINGS_COMMANDS
# For Tizen Local API: Uses full set of commands
SAMSUNG_KEY_MAP = {
    # Navigation (SmartThings compatible)
    "UP": "UP",
    "DOWN": "DOWN",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "ENTER": "OK",  # SmartThings uses OK instead of ENTER
    "OK": "OK",
    "RETURN": "BACK",  # SmartThings uses BACK instead of RETURN
    "BACK": "BACK",
    
    # Menu (SmartThings compatible)
    "HOME": "HOME",
    "MENU": "MENU",
    "EXIT": "EXIT",
    
    # Volume (SmartThings: only MUTE is supported)
    "MUTE": "MUTE",
    "VOLUME_UP": "VOLUP",  # Only works with Tizen Local
    "VOLUME_DOWN": "VOLDOWN",  # Only works with Tizen Local
    "VOLUP": "VOLUP",  # Only works with Tizen Local
    "VOLDOWN": "VOLDOWN",  # Only works with Tizen Local
    
    # Playback (SmartThings compatible)
    "PLAY": "PLAY",
    "PAUSE": "PAUSE",
    "STOP": "STOP",
    "REWIND": "REWIND",
    "FAST_FORWARD": "FF",
    "FF": "FF",
    "PLAY_BACK": "PLAY_BACK",
    
    # Source (SmartThings compatible)
    "SOURCE": "SOURCE",
    
    # Power (Only works with Tizen Local)
    "POWER": "POWER",
    "POWEROFF": "POWEROFF",
    
    # Channel (Only works with Tizen Local)
    "CHANNEL_UP": "CHUP",
    "CHANNEL_DOWN": "CHDOWN",
    "CHUP": "CHUP",
    "CHDOWN": "CHDOWN",
    "PRECH": "PRECH",
    
    # HDMI (Only works with Tizen Local)
    "HDMI": "HDMI",
    "HDMI1": "HDMI1",
    "HDMI2": "HDMI2",
    "HDMI3": "HDMI3",
    "HDMI4": "HDMI4",
    
    # Guide (Only works with Tizen Local)
    "GUIDE": "GUIDE",
    "CH_LIST": "CH_LIST",
    "TOOLS": "TOOLS",
    "INFO": "INFO",
    
    # Color buttons (Only works with Tizen Local)
    "RED": "RED",
    "GREEN": "GREEN",
    "YELLOW": "YELLOW",
    "BLUE": "BLUE",
    
    # Numbers (Only works with Tizen Local)
    "0": "NUM0",
    "1": "NUM1",
    "2": "NUM2",
    "3": "NUM3",
    "4": "NUM4",
    "5": "NUM5",
    "6": "NUM6",
    "7": "NUM7",
    "8": "NUM8",
    "9": "NUM9",
    "NUM0": "NUM0",
    "NUM1": "NUM1",
    "NUM2": "NUM2",
    "NUM3": "NUM3",
    "NUM4": "NUM4",
    "NUM5": "NUM5",
    "NUM6": "NUM6",
    "NUM7": "NUM7",
    "NUM8": "NUM8",
    "NUM9": "NUM9",
    
    # Additional (Only works with Tizen Local)
    "PICTURE_MODE": "PICTURE_MODE",
    "SOUND_MODE": "SOUND_MODE",
    "SLEEP": "SLEEP",
    "ASPECT": "ASPECT",
    "CAPTION": "CAPTION",
    "SETTINGS": "SETTINGS",
    "E_MANUAL": "E_MANUAL",
    "SEARCH": "SEARCH",
    "REC": "REC",
}

SUPPORTED_COMMANDS = list(SAMSUNG_KEY_MAP.keys())

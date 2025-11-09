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
CONF_LOCAL_IP = "local_ip"
CONF_LOCAL_PSK = "local_psk"
CONF_TIMEOUT = "timeout"

# Defaults
DEFAULT_TIMEOUT = 10
DEFAULT_API_METHOD = "smartthings"

# API Methods
class APIMethod(Enum):
    """API connection methods."""
    SMARTTHINGS = "smartthings"
    TIZEN_LOCAL = "tizen_local"


# Samsung TV Key Codes for SmartThings API
# These are the codes that work with samsungvd.remoteControl capability
SAMSUNG_KEY_MAP = {
    # Power
    "POWER": "POWER",
    "POWEROFF": "POWEROFF",
    
    # Navigation
    "UP": "UP",
    "DOWN": "DOWN",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "ENTER": "ENTER",
    "RETURN": "RETURN",
    "BACK": "RETURN",  # Alias
    
    # Menu
    "HOME": "HOME",
    "MENU": "MENU",
    "TOOLS": "TOOLS",
    "INFO": "INFO",
    "EXIT": "EXIT",
    
    # Volume
    "VOLUME_UP": "VOLUP",
    "VOLUME_DOWN": "VOLDOWN",
    "MUTE": "MUTE",
    "VOLUP": "VOLUP",
    "VOLDOWN": "VOLDOWN",
    
    # Channel
    "CHANNEL_UP": "CHUP",
    "CHANNEL_DOWN": "CHDOWN",
    "CHUP": "CHUP",
    "CHDOWN": "CHDOWN",
    "PRECH": "PRECH",  # Previous channel
    
    # Playback
    "PLAY": "PLAY",
    "PAUSE": "PAUSE",
    "STOP": "STOP",
    "REWIND": "REWIND",
    "FAST_FORWARD": "FF",
    "FF": "FF",
    "REC": "REC",
    
    # Source
    "SOURCE": "SOURCE",
    "HDMI": "HDMI",
    "HDMI1": "HDMI1",
    "HDMI2": "HDMI2",
    "HDMI3": "HDMI3",
    "HDMI4": "HDMI4",
    
    # Guide
    "GUIDE": "GUIDE",
    "CH_LIST": "CH_LIST",
    
    # Color buttons
    "RED": "RED",
    "GREEN": "GREEN",
    "YELLOW": "YELLOW",
    "BLUE": "BLUE",
    
    # Numbers
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
    
    # Additional
    "PICTURE_MODE": "PICTURE_MODE",
    "SOUND_MODE": "SOUND_MODE",
    "SLEEP": "SLEEP",
    "ASPECT": "ASPECT",
    "CAPTION": "CAPTION",
    "SETTINGS": "SETTINGS",
    "E_MANUAL": "E_MANUAL",
    "SEARCH": "SEARCH",
}

SUPPORTED_COMMANDS = list(SAMSUNG_KEY_MAP.keys())

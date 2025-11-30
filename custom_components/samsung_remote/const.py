"""Constants for Samsung Remote integration."""

import logging

# Integration domain
DOMAIN = "samsung_remote"

# Logger
LOGGER = logging.getLogger(__package__)

# Configuration keys
CONF_API_METHOD = "api_method"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_SMARTTHINGS_TOKEN = "smartthings_token"
CONF_LOCAL_IP = "local_ip"
CONF_LOCAL_PSK = "local_psk"

# Defaults
DEFAULT_API_METHOD = "smartthings"
DEFAULT_TIMEOUT = 10

# SmartThings commands (limited set supported by SmartThings API)
SMARTTHINGS_COMMANDS = {
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "OK",
    "BACK",
    "HOME",
    "MENU",
    "EXIT",
    "MUTE",
    "PLAY",
    "PAUSE",
    "STOP",
    "REWIND",
    "FF",
    "PLAY_BACK",
    "SOURCE",
}

# Samsung TV key mapping
SAMSUNG_KEY_MAP = {
    # Power
    "POWER": "KEY_POWER",
    "POWEROFF": "KEY_POWEROFF",
    
    # Volume
    "VOLUP": "KEY_VOLUP",
    "VOLDOWN": "KEY_VOLDOWN",
    "MUTE": "KEY_MUTE",
    
    # Channels
    "CHUP": "KEY_CHUP",
    "CHDOWN": "KEY_CHDOWN",
    "PRECH": "KEY_PRECH",
    
    # Navigation
    "UP": "KEY_UP",
    "DOWN": "KEY_DOWN",
    "LEFT": "KEY_LEFT",
    "RIGHT": "KEY_RIGHT",
    "OK": "KEY_ENTER",
    "ENTER": "KEY_ENTER",
    "RETURN": "KEY_RETURN",
    "BACK": "KEY_RETURN",
    "EXIT": "KEY_EXIT",
    "HOME": "KEY_HOME",
    "MENU": "KEY_MENU",
    
    # Playback
    "PLAY": "KEY_PLAY",
    "PAUSE": "KEY_PAUSE",
    "STOP": "KEY_STOP",
    "REWIND": "KEY_REWIND",
    "FF": "KEY_FF",
    "PLAY_BACK": "KEY_PLAY_BACK",
    
    # Source
    "SOURCE": "KEY_SOURCE",
    "HDMI": "KEY_HDMI",
    "HDMI1": "KEY_HDMI1",
    "HDMI2": "KEY_HDMI2",
    "HDMI3": "KEY_HDMI3",
    "HDMI4": "KEY_HDMI4",
    
    # Numbers
    "NUM0": "KEY_0",
    "NUM1": "KEY_1",
    "NUM2": "KEY_2",
    "NUM3": "KEY_3",
    "NUM4": "KEY_4",
    "NUM5": "KEY_5",
    "NUM6": "KEY_6",
    "NUM7": "KEY_7",
    "NUM8": "KEY_8",
    "NUM9": "KEY_9",
    
    # Color buttons
    "RED": "KEY_RED",
    "GREEN": "KEY_GREEN",
    "YELLOW": "KEY_YELLOW",
    "BLUE": "KEY_BLUE",
    
    # Additional
    "GUIDE": "KEY_GUIDE",
    "CH_LIST": "KEY_CH_LIST",
    "TOOLS": "KEY_TOOLS",
    "INFO": "KEY_INFO",
    "PICTURE_MODE": "KEY_PICTURE_MODE",
    "SOUND_MODE": "KEY_SOUND_MODE",
    "SLEEP": "KEY_SLEEP",
    "ASPECT": "KEY_ASPECT",
    "CAPTION": "KEY_CAPTION",
    "SETTINGS": "KEY_SETTINGS",
    "E_MANUAL": "KEY_E_MANUAL",
    "SEARCH": "KEY_SEARCH",
    "REC": "KEY_REC",
}

# All supported commands (combination of SmartThings and Tizen)
SUPPORTED_COMMANDS = list(SAMSUNG_KEY_MAP.keys())

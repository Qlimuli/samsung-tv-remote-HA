"""Constants for the Samsung Remote integration."""

DOMAIN = "samsung_remote"

# Connection methods
CONNECTION_METHOD_SMARTTHINGS = "smartthings"
CONNECTION_METHOD_LOCAL = "local"

# SmartThings API
SMARTTHINGS_API_BASE = "https://api.smartthings.com/v1"
SMARTTHINGS_DOMAIN = "smartthings"

# Configuration
CONF_CONNECTION_METHOD = "connection_method"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_ACCESS_TOKEN = "access_token"

# Attributes
ATTR_COMMAND = "command"
ATTR_DEVICE_ID = "device_id"

# Services
SERVICE_SEND_COMMAND = "send_command"
SERVICE_REFRESH_TOKEN = "refresh_oauth_token"

# Default values
DEFAULT_NAME = "Samsung TV"
DEFAULT_PORT = 8001
DEFAULT_TIMEOUT = 3

# Supported commands mapping
SMARTTHINGS_COMMANDS = {
    # Navigation
    "UP": "up",
    "DOWN": "down",
    "LEFT": "left",
    "RIGHT": "right",
    "OK": "select",
    "ENTER": "select",
    "BACK": "back",
    "HOME": "home",
    "MENU": "menu",
    "EXIT": "exit",
    
    # Volume
    "MUTE": "mute",
    
    # Playback
    "PLAY": "play",
    "PAUSE": "pause",
    "STOP": "stop",
    "REWIND": "rewind",
    "FF": "fastForward",
    "PLAY_BACK": "rewind",
    
    # Source
    "SOURCE": "selectInputSource",
}

# Tizen key mapping (für local connection)
TIZEN_KEYS = {
    "POWER": "KEY_POWER",
    "POWEROFF": "KEY_POWEROFF",
    "UP": "KEY_UP",
    "DOWN": "KEY_DOWN",
    "LEFT": "KEY_LEFT",
    "RIGHT": "KEY_RIGHT",
    "OK": "KEY_ENTER",
    "ENTER": "KEY_ENTER",
    "RETURN": "KEY_RETURN",
    "BACK": "KEY_RETURN",
    "HOME": "KEY_HOME",
    "MENU": "KEY_MENU",
    "GUIDE": "KEY_GUIDE",
    "INFO": "KEY_INFO",
    "EXIT": "KEY_EXIT",
    "SOURCE": "KEY_SOURCE",
    
    # Volume
    "VOLUME_UP": "KEY_VOLUP",
    "VOLUME_DOWN": "KEY_VOLDOWN",
    "MUTE": "KEY_MUTE",
    
    # Channel
    "CHANNEL_UP": "KEY_CHUP",
    "CHANNEL_DOWN": "KEY_CHDOWN",
    "PRECH": "KEY_PRECH",
    
    # Playback
    "PLAY": "KEY_PLAY",
    "PAUSE": "KEY_PAUSE",
    "STOP": "KEY_STOP",
    "REWIND": "KEY_REWIND",
    "FF": "KEY_FF",
    "REC": "KEY_REC",
    
    # Numbers
    "0": "KEY_0",
    "1": "KEY_1",
    "2": "KEY_2",
    "3": "KEY_3",
    "4": "KEY_4",
    "5": "KEY_5",
    "6": "KEY_6",
    "7": "KEY_7",
    "8": "KEY_8",
    "9": "KEY_9",
    
    # Color buttons
    "RED": "KEY_RED",
    "GREEN": "KEY_GREEN",
    "YELLOW": "KEY_YELLOW",
    "BLUE": "KEY_BLUE",
    
    # HDMI
    "HDMI": "KEY_HDMI",
    "HDMI1": "KEY_HDMI1",
    "HDMI2": "KEY_HDMI2",
    "HDMI3": "KEY_HDMI3",
    "HDMI4": "KEY_HDMI4",
    
    # Special
    "TOOLS": "KEY_TOOLS",
    "CH_LIST": "KEY_CH_LIST",
    "PICTURE_MODE": "KEY_PICTURE_SIZE",
    "SOUND_MODE": "KEY_SOUND_MODE",
    "SLEEP": "KEY_SLEEP",
    "ASPECT": "KEY_ASPECT",
    "CAPTION": "KEY_CAPTION",
    "SETTINGS": "KEY_SETTINGS",
    "E_MANUAL": "KEY_CONTENTS",
    "SEARCH": "KEY_SEARCH",
}

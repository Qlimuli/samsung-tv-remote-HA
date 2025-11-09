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


# Samsung TV Key Codes
SAMSUNG_KEY_MAP = {
    "POWER": "KEY_POWER",
    "HOME": "KEY_HOME",
    "BACK": "KEY_BACK",
    "VOLUME_UP": "KEY_VOLUME_UP",
    "VOLUME_DOWN": "KEY_VOLUME_DOWN",
    "CHANNEL_UP": "KEY_CH_UP",
    "CHANNEL_DOWN": "KEY_CH_DOWN",
    "UP": "KEY_UP",
    "DOWN": "KEY_DOWN",
    "LEFT": "KEY_LEFT",
    "RIGHT": "KEY_RIGHT",
    "ENTER": "KEY_ENTER",
    "MENU": "KEY_MENU",
    "SOURCE": "KEY_SOURCE",
    "GUIDE": "KEY_GUIDE",
    "INFO": "KEY_INFO",
    "EXIT": "KEY_EXIT",
    "RED": "KEY_RED",
    "GREEN": "KEY_GREEN",
    "YELLOW": "KEY_YELLOW",
    "BLUE": "KEY_BLUE",
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
    "PLAY": "KEY_PLAY",
    "PAUSE": "KEY_PAUSE",
    "STOP": "KEY_STOP",
    "REWIND": "KEY_REWIND",
    "FAST_FORWARD": "KEY_FAST_FORWARD",
}

SUPPORTED_COMMANDS = list(SAMSUNG_KEY_MAP.keys())

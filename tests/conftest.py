"""Shared pytest configuration and fixtures."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.fixture
def hass():
    """Return a Home Assistant instance."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    hass = HomeAssistant(loop=loop)
    yield hass
    loop.run_until_complete(hass.async_block_till_done())
    hass.data.clear()


@pytest.fixture
def mock_smartthings_api():
    """Mock SmartThings API."""
    api = AsyncMock()
    api.validate_token = AsyncMock(return_value=True)
    api.get_devices = AsyncMock(return_value=[
        {
            "deviceId": "device-123",
            "label": "Living Room TV",
            "deviceType": "SMARTTV",
            "components": [{"capabilities": [{"id": "remoteControl"}]}]
        }
    ])
    api.send_command = AsyncMock(return_value=True)
    api.close = AsyncMock()
    return api


@pytest.fixture
def mock_tizen_api():
    """Mock Tizen local API."""
    api = AsyncMock()
    api.validate_connection = AsyncMock(return_value=True)
    api.send_command = AsyncMock(return_value=True)
    api.close = AsyncMock()
    return api

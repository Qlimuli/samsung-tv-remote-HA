"""Tests for remote entity."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.remote import RemoteEntity
from homeassistant.core import HomeAssistant

from custom_components.samsung_remote.remote import SamsungRemote
from custom_components.samsung_remote.const import DOMAIN


@pytest.mark.asyncio
async def test_samsung_remote_send_command(hass: HomeAssistant, mock_smartthings_api):
    """Test sending command."""
    config_entry = MagicMock()
    config_entry.data = {
        "api_method": "smartthings",
        "device_id": "device-123",
        "device_name": "Living Room TV"
    }
    config_entry.entry_id = "entry-123"
    
    remote = SamsungRemote(
        hass=hass,
        config_entry=config_entry,
        api=mock_smartthings_api,
        device_id="device-123",
        device_name="Living Room TV"
    )
    
    await remote.async_send_command(["POWER"])
    mock_smartthings_api.send_command.assert_called_once_with("device-123", "POWER")


@pytest.mark.asyncio
async def test_samsung_remote_multiple_commands(hass: HomeAssistant, mock_smartthings_api):
    """Test sending multiple commands."""
    config_entry = MagicMock()
    config_entry.data = {"api_method": "smartthings"}
    config_entry.entry_id = "entry-123"
    
    remote = SamsungRemote(
        hass=hass,
        config_entry=config_entry,
        api=mock_smartthings_api,
        device_id="device-123",
        device_name="Living Room TV"
    )
    
    await remote.async_send_command(["VOLUME_UP", "VOLUME_UP", "VOLUME_UP"])
    assert mock_smartthings_api.send_command.call_count == 3


@pytest.mark.asyncio
async def test_samsung_remote_attributes(hass: HomeAssistant, mock_smartthings_api):
    """Test remote attributes."""
    config_entry = MagicMock()
    config_entry.data = {"api_method": "smartthings"}
    config_entry.entry_id = "entry-123"
    
    remote = SamsungRemote(
        hass=hass,
        config_entry=config_entry,
        api=mock_smartthings_api,
        device_id="device-123",
        device_name="Living Room TV"
    )
    
    attrs = remote.extra_state_attributes
    assert "supported_commands" in attrs
    assert "POWER" in attrs["supported_commands"]
    assert len(attrs["supported_commands"]) > 20

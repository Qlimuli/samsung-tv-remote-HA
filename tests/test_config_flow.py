"""Tests for config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.samsung_remote.config_flow import ConfigFlow
from custom_components.samsung_remote.const import (
    CONF_API_METHOD,
    CONF_DEVICE_ID,
    CONF_LOCAL_IP,
    CONF_SMARTTHINGS_TOKEN,
    DOMAIN,
)


async def test_config_flow_smartthings(hass: HomeAssistant, mock_smartthings_api):
    """Test SmartThings config flow."""
    with patch("custom_components.samsung_remote.config_flow.SmartThingsAPI") as mock_api_class:
        mock_api_class.return_value = mock_smartthings_api
        
        flow = ConfigFlow()
        flow.hass = hass
        
        # Step 1: User
        result = await flow.async_step_user({CONF_API_METHOD: "smartthings"})
        assert result["type"] == "form"
        assert result["step_id"] == "smartthings"
        
        # Step 2: SmartThings
        result = await flow.async_step_smartthings({
            CONF_SMARTTHINGS_TOKEN: "test-token"
        })
        assert result["type"] == "form"
        assert result["step_id"] == "select_device"
        
        # Step 3: Select device
        result = await flow.async_step_select_device({
            CONF_DEVICE_ID: "device-123"
        })
        assert result["type"] == "create_entry"
        assert result["title"] == "Living Room TV"


async def test_config_flow_tizen_local(hass: HomeAssistant, mock_tizen_api):
    """Test Tizen local config flow."""
    with patch("custom_components.samsung_remote.config_flow.TizenLocalAPI") as mock_api_class:
        mock_api_class.return_value = mock_tizen_api
        
        flow = ConfigFlow()
        flow.hass = hass
        
        result = await flow.async_step_user({CONF_API_METHOD: "tizen_local"})
        assert result["type"] == "form"
        assert result["step_id"] == "tizen_local"
        
        result = await flow.async_step_tizen_local({
            CONF_LOCAL_IP: "192.168.1.100"
        })
        assert result["type"] == "create_entry"


async def test_smartthings_invalid_token(hass: HomeAssistant):
    """Test invalid SmartThings token."""
    mock_api = AsyncMock()
    mock_api.validate_token = AsyncMock(return_value=False)
    
    with patch("custom_components.samsung_remote.config_flow.SmartThingsAPI") as mock_api_class:
        mock_api_class.return_value = mock_api
        
        flow = ConfigFlow()
        flow.hass = hass
        
        await flow.async_step_user({CONF_API_METHOD: "smartthings"})
        result = await flow.async_step_smartthings({
            CONF_SMARTTHINGS_TOKEN: "invalid-token"
        })
        
        assert result["type"] == "form"
        assert result["errors"]["base"] == "invalid_token"

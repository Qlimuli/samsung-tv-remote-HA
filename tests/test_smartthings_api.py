"""Tests for SmartThings API client."""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from custom_components.samsung_remote.api.smartthings import SmartThingsAPI


@pytest.mark.asyncio
async def test_smartthings_validate_token_success():
    """Test successful token validation."""
    mock_hass = MagicMock()
    api = SmartThingsAPI(mock_hass, "test-token")
    
    with patch.object(api, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"items": []}
        result = await api.validate_token()
        assert result is True


@pytest.mark.asyncio
async def test_smartthings_validate_token_failure():
    """Test failed token validation."""
    mock_hass = MagicMock()
    api = SmartThingsAPI(mock_hass, "invalid-token")
    
    with patch.object(api, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("Invalid token")
        result = await api.validate_token()
        assert result is False


@pytest.mark.asyncio
async def test_smartthings_get_devices():
    """Test fetching devices."""
    mock_hass = MagicMock()
    api = SmartThingsAPI(mock_hass, "test-token")
    
    mock_devices = {
        "items": [
            {
                "deviceId": "device-123",
                "label": "Living Room TV",
                "deviceType": "SMARTTV",
                "components": [{"capabilities": [{"id": "remoteControl"}]}]
            }
        ]
    }
    
    with patch.object(api, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_devices
        devices = await api.get_devices()
        assert len(devices) == 1
        assert devices[0]["deviceId"] == "device-123"


@pytest.mark.asyncio
async def test_smartthings_send_command():
    """Test sending command."""
    mock_hass = MagicMock()
    api = SmartThingsAPI(mock_hass, "test-token")
    
    with patch.object(api, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {}
        result = await api.send_command("device-123", "POWER")
        assert result is True
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_smartthings_send_command_failure():
    """Test sending command failure."""
    mock_hass = MagicMock()
    api = SmartThingsAPI(mock_hass, "test-token")
    
    with patch.object(api, "_request", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("Network error")
        result = await api.send_command("device-123", "POWER")
        assert result is False


@pytest.mark.asyncio
async def test_smartthings_retry_logic():
    """Test retry logic on rate limit."""
    mock_hass = MagicMock()
    api = SmartThingsAPI(mock_hass, "test-token")
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"items": []})
        mock_request.return_value.__aenter__.return_value = mock_response
        
        result = await api._request("GET", "/devices")
        assert "items" in result


@pytest.mark.asyncio
async def test_smartthings_is_tv_device():
    """Test TV device detection."""
    mock_hass = MagicMock()
    api = SmartThingsAPI(mock_hass, "test-token")
    
    tv_device = {
        "deviceType": "SMARTTV",
        "components": [{"capabilities": [{"id": "remoteControl"}]}]
    }
    assert api._is_tv_device(tv_device) is True
    
    non_tv_device = {
        "deviceType": "LIGHTBULB",
        "components": [{"capabilities": [{"id": "switch"}]}]
    }
    assert api._is_tv_device(non_tv_device) is False

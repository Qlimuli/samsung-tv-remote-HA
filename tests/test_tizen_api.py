"""Tests for Tizen local API client."""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from custom_components.samsung_remote.api.tizen_local import TizenLocalAPI


@pytest.mark.asyncio
async def test_tizen_validate_connection_success():
    """Test successful connection validation."""
    api = TizenLocalAPI("192.168.1.100")
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await api.validate_connection()
        assert result is True


@pytest.mark.asyncio
async def test_tizen_validate_connection_failure():
    """Test failed connection validation."""
    api = TizenLocalAPI("192.168.1.100")
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        result = await api.validate_connection()
        assert result is False


@pytest.mark.asyncio
async def test_tizen_send_command():
    """Test sending command."""
    api = TizenLocalAPI("192.168.1.100")
    
    result = await api.send_command("POWER")
    assert result is True


@pytest.mark.asyncio
async def test_tizen_send_command_with_psk():
    """Test sending command with PSK."""
    api = TizenLocalAPI("192.168.1.100", psk="test-psk")
    
    result = await api.send_command("VOLUME_UP")
    assert result is True


@pytest.mark.asyncio
async def test_tizen_close_session():
    """Test closing session."""
    api = TizenLocalAPI("192.168.1.100")
    
    with patch("aiohttp.ClientSession.close") as mock_close:
        mock_close.return_value = AsyncMock()
        await api.close()

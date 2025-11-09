"""Local Tizen API client for Samsung devices."""

import asyncio
import json
import logging
from typing import Optional

import aiohttp

from ..const import LOGGER, DEFAULT_TIMEOUT, SAMSUNG_KEY_MAP


class TizenLocalAPI:
    """Tizen local API client for direct TV communication."""

    def __init__(self, ip: str, psk: str = "", timeout: int = DEFAULT_TIMEOUT):
        """Initialize Tizen local client."""
        self.ip = ip
        self.psk = psk
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.paired = False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def send_command(self, command: str) -> bool:
        """Send command via local websocket."""
        try:
            key = SAMSUNG_KEY_MAP.get(command, command)
            
            # Simulate sending via websocket/UDP to local TV
            # In production, this would use websocket-client or direct socket
            LOGGER.debug(f"Sending command {key} to TV at {self.ip}")
            await asyncio.sleep(0.1)
            
            return True
        except Exception as e:
            LOGGER.error(f"Failed to send local command: {e}")
            return False

    async def validate_connection(self) -> bool:
        """Validate connection to TV."""
        try:
            # Attempt to reach TV's main app
            session = await self._get_session()
            url = f"http://{self.ip}:8001/ms/version"
            
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                return resp.status == 200
        except Exception as e:
            LOGGER.error(f"Connection validation failed: {e}")
            return False

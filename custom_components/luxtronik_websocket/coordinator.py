"""Coordinator for monitoring a luxtronik heatpump."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .luxsocket import LuxSocket, LuxValue

_LOGGER = logging.getLogger(__name__)


class LuxtronikCoordinator(DataUpdateCoordinator[dict[str, LuxValue]]):
    """Luxtronik coordinator."""

    def __init__(
        self, hass: HomeAssistant, host: str, port: str, password: str
    ) -> None:
        """Initialize luxtronik coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
            always_update=False,
        )
        self._socket = LuxSocket(host, port, password)

    async def _async_update_data(self) -> dict[str, LuxValue]:
        """Fetch luxtronik information."""
        try:
            await self._socket.get_data()
        except TimeoutError as error:
            raise UpdateFailed(
                f"Can not retrieve luxtronik statistics {error}"
            ) from error

        return self._socket.data

    async def get_items(self):
        """Get sensor items fetched from Luxtronik."""
        if self._socket.data is None:
            await self._socket.get_data()
        return self._socket.data.items()

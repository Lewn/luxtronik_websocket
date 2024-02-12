"""The Luxtronik Websocket integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CannotConnect
from .luxsocket import LuxSocket

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Luxtronik Websocket from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    luxSocket = LuxSocket(
        entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_PASSWORD]
    )
    if not await luxSocket.test_connection():
        raise CannotConnect

    hass.data[DOMAIN][entry.entry_id] = luxSocket

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

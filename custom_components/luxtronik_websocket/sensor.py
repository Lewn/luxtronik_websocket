"""Sensor for monitoring a luxtronik heat pump."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LuxtronikCoordinator

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:text-short"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform from config entry."""

    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    password = entry.data[CONF_PASSWORD]
    coordinator = LuxtronikCoordinator(hass, host, port, password)
    await coordinator.async_config_entry_first_refresh()

    keys = await coordinator.get_keys()
    async_add_entities(
        LuxtronikEntity(
            SensorEntityDescription(
                key=key,
                icon=ICON,
                name=key.split("_")[-1],
                has_entity_name=True,
            ),
            entry.entry_id,
            coordinator,
        )
        for key in keys
    )


class LuxtronikEntity(CoordinatorEntity[LuxtronikCoordinator], SensorEntity):
    """Luxtronik sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        description: SensorEntityDescription,
        entry_id: str,
        coordinator: LuxtronikCoordinator,
    ) -> None:
        """Initialize the Luxtronik sensor."""
        super().__init__(coordinator)
        base_name = description.key.split("_")[-1]
        _LOGGER.warning(
            "Adding entry: %s",
            repr(
                {
                    "entry_id": entry_id,
                    "base_name": base_name,
                    "description.key": description.key,
                }
            ),
        )
        self._attr_unique_id = f"{entry_id}-{description.key}"
        self.entity_id = f"sensor.luxtronic_websocket_{description.key}".lower()
        self.entity_description = description
        self._attr_device_info = DeviceInfo(
            entry_type=None,
            identifiers={(DOMAIN, entry_id)},
            name="Luxtronik",
        )

    @property
    def native_value(self) -> str:
        """Return the value of the sensor."""
        value: str = self.coordinator.data[self.entity_description.key]
        return value

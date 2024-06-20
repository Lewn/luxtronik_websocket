"""Sensor for monitoring a luxtronik heat pump."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LuxtronikCoordinator
from .luxsocket import LuxValue

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:text-short"

UNITS_TO_CLASS = {
    "°C": (SensorDeviceClass.TEMPERATURE, "°C", None),
    "K": (SensorDeviceClass.TEMPERATURE, "K", None),
    "V": (SensorDeviceClass.VOLTAGE, "V", None),
    "h": (SensorDeviceClass.DURATION, "h", None),
    "min": (SensorDeviceClass.DURATION, "min", None),
    "Hz": (SensorDeviceClass.FREQUENCY, "Hz", None),
    "l/h": (SensorDeviceClass.VOLUME_FLOW_RATE, "L/min", 1 / 60),
    "bar": (SensorDeviceClass.PRESSURE, "bar", None),
    "%": (None, "%", None),
    "kW": (SensorDeviceClass.POWER, "kW", None),
    "kWh": (SensorDeviceClass.ENERGY, "kWh", None),
    "s": (SensorDeviceClass.DURATION, "s", None),
}


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

    items = await coordinator.get_items()
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
            value.unit,
        )
        for key, value in items
        # Do not process timestamps
        # Future work: actually detect timestamps instead of just a colon
        if ":" not in key.split("_")[-1]
    )


class LuxtronikEntity(CoordinatorEntity[LuxtronikCoordinator], SensorEntity):
    """Luxtronik sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        description: SensorEntityDescription,
        entry_id: str,
        coordinator: LuxtronikCoordinator,
        unit: str,
    ) -> None:
        """Initialize the Luxtronik sensor."""
        super().__init__(coordinator)
        base_name = description.key.split("_")[-1]
        _LOGGER.info(
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
        self._conversion = None
        if unit in UNITS_TO_CLASS:
            device_class, unit, conversion = UNITS_TO_CLASS[unit]
            if device_class is not None:
                self.device_class = device_class
            if unit is not None:
                self.native_unit_of_measurement = unit
            if conversion is not None:
                self._conversion = conversion

    @property
    def native_value(self) -> float | str:
        """Return the value of the sensor."""
        value: LuxValue = self.coordinator.data.get(self.entity_description.key, None)
        if value is None or value.value is None:
            return None
        if self._conversion:
            return self._conversion * value.value
        return value.value

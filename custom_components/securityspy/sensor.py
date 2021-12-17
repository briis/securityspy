""" This component provides Sensors for SecuritySpy."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_DIAGNOSTIC
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from .entity import SecuritySpyEntity

from .const import (
    DOMAIN,
    RECORDING_TYPE_ACTION,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_MOTION,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "motion_recording": [
        "Motion Recording",
        None,
        ["video-outline", "video-off-outline"],
        RECORDING_TYPE_MOTION,
    ],
    "continuous_recording": [
        "Continuous Recording",
        None,
        ["video-outline", "video-off-outline"],
        RECORDING_TYPE_CONTINUOUS,
    ],
    "actions": [
        "Actions Enabled",
        None,
        ["script-text-play", "script-text"],
        RECORDING_TYPE_ACTION,
    ],
}

_SENSOR_NAME = 0
_SENSOR_UNITS = 1
_SENSOR_ICONS = 2
_SENSOR_TYPE = 3

_ICON_ON = 0
_ICON_OFF = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """A SecsuritySpy Sensor."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    sensors = []
    for sensor in SENSOR_TYPES:
        for device_id in secspy_data.data:
            sensors.append(
                SecuritySpySensor(
                    secspy_object, secspy_data, server_info, device_id, sensor
                )
            )
            _LOGGER.debug("SECURITYSPY SENSOR CREATED: %s", sensor)

    async_add_entities(sensors)

    return True


class SecuritySpySensor(SecuritySpyEntity, Entity):
    """A SecuritySpy Sensor."""

    def __init__(self, secspy_object, secspy_data, server_info, device_id, sensor):
        """Initialize an Unifi Protect sensor."""
        super().__init__(secspy_object, secspy_data, server_info, device_id, sensor)
        sensor_type = SENSOR_TYPES[sensor]
        self._name = f"{sensor_type[_SENSOR_NAME]} {self._device_data['name']}"
        self._units = sensor_type[_SENSOR_UNITS]
        self._icons = sensor_type[_SENSOR_ICONS]
        self._sensor_type = sensor_type[_SENSOR_TYPE]
        self._attr_entity_category = ENTITY_CATEGORY_DIAGNOSTIC

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._sensor_type == RECORDING_TYPE_ACTION:
            return self._device_data["recording_mode_a"]
        if self._sensor_type == RECORDING_TYPE_CONTINUOUS:
            return self._device_data["recording_mode_c"]
        if self._sensor_type == RECORDING_TYPE_MOTION:
            return self._device_data["recording_mode_m"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        icon_id = _ICON_ON if self.state else _ICON_OFF
        return f"mdi:{self._icons[icon_id]}"

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._units

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

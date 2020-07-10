""" This component provides Sensors for SecuritySpy."""

import logging

from homeassistant.helpers.entity import Entity
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from pysecurityspy import (
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_NEVER,
)
from .entity import SecuritySpyEntity
from .const import (
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    ATTR_BRAND,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "motion_recording": ["Motion Recording", None, "video-outline,video-off-outline"]
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A SecsuritySpy Sensor."""
    secspy = hass.data[DOMAIN][entry.entry_id]["secspy"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    nvr = hass.data[DOMAIN][entry.entry_id]["nvr"]
    if not coordinator.data:
        return

    sensors = []
    for sensor in SENSOR_TYPES:
        for camera in coordinator.data:
            sensors.append(SecuritySpySensor(secspy, coordinator, nvr, camera, sensor))
            _LOGGER.debug("SECURITYSPY SENSOR CREATED: %s", sensor)

    async_add_entities(sensors, True)

    return True


class SecuritySpySensor(SecuritySpyEntity, Entity):
    """A SecuritySpy Sensor."""

    def __init__(self, secspy, coordinator, nvr, camera_id, sensor):
        """Initialize an Unifi Protect sensor."""
        super().__init__(secspy, coordinator, nvr, camera_id, sensor)
        self._name = f"{SENSOR_TYPES[sensor][0]} {self._camera_data['name']}"
        self._units = SENSOR_TYPES[sensor][1]
        self._icons = SENSOR_TYPES[sensor][2]

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._camera_data["recording_mode"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        icons = self._icons.split(",")
        return (
            f"mdi:{icons[0]}"
            if self.state != RECORDING_MODE_NEVER
            else f"mdi:{icons[1]}"
        )

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._units

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_BRAND: DEFAULT_BRAND,
        }

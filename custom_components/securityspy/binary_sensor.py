""" This component provides binary sensors for SecuritySpy."""
import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LAST_TRIP_TIME
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_EVENT_LENGTH,
    ATTR_EVENT_OBJECT,
    DEFAULT_ATTRIBUTION,
    DEVICE_TYPE_DOORBELL,
    DEVICE_TYPE_MOTION,
    DOMAIN,
)
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)

SECSPY_TO_HASS_DEVICE_CLASS = {
    DEVICE_TYPE_DOORBELL: DEVICE_CLASS_OCCUPANCY,
    DEVICE_TYPE_MOTION: DEVICE_CLASS_MOTION,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Setup Binary Sensors."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    sensors = []
    for device_id in secspy_data.data:
        device_data = secspy_data.data[device_id]
        sensors.append(
            SecuritySpyBinarySensor(
                secspy_object, secspy_data, server_info, device_id, DEVICE_TYPE_MOTION
            )
        )
        _LOGGER.debug("SECURITYSPY MOTION SENSOR CREATED: %s", device_data["name"])

    async_add_entities(sensors)

    return True


class SecuritySpyBinarySensor(SecuritySpyEntity, BinarySensorEntity):
    """A SecuritySpy Binary Sensor."""

    def __init__(self, secspy_object, secspy_data, server_info, device_id, sensor_type):
        """Initialize the Binary Sensor."""
        super().__init__(
            secspy_object, secspy_data, server_info, device_id, sensor_type
        )
        self._name = f"{sensor_type.capitalize()} {self._device_data['name']}"
        self._device_class = SECSPY_TO_HASS_DEVICE_CLASS.get(sensor_type)

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._sensor_type != DEVICE_TYPE_DOORBELL:
            return self._device_data["event_on"]
        return self._device_data["event_ring_on"]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_LAST_TRIP_TIME: self._device_data["last_motion"],
            ATTR_EVENT_LENGTH: self._device_data["event_length"],
            ATTR_EVENT_OBJECT: self._device_data["event_object"],
        }

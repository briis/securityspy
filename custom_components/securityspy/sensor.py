""" This component provides Sensors for SecuritySpy."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType
from .entity import SecuritySpyEntity

from .const import (
    ATTR_BRAND,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DEVICES_WITH_CAMERA,
    DOMAIN,
    RECORDING_TYPE_OFF,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "motion_recording": [
        "Motion Recording",
        None,
        ["video-outline,video-off-outline"],
        DEVICES_WITH_CAMERA,
    ],
}

_SENSOR_NAME = 0
_SENSOR_UNITS = 1
_SENSOR_ICONS = 2
_SENSOR_MODEL = 3

_ICON_ON = 0
_ICON_OFF = 1


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A SecsuritySpy Sensor."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    sensors = []
    for sensor, sensor_type in SENSOR_TYPES.items():
        for device_id in secspy_data.data:
            if secspy_data.data[device_id].get("type") in sensor_type[_SENSOR_MODEL]:
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

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._device_data["recording_mode"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        icon_id = _ICON_ON if self.state != RECORDING_TYPE_OFF else _ICON_OFF
        return f"mdi:{self._icons[icon_id]}"

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

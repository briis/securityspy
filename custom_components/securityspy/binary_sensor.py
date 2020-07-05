""" This component provides binary sensors for SecuritySpy."""
import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_MOTION,
)
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_LAST_TRIP_TIME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.typing import HomeAssistantType
from pysecurityspy import MOTION_TRIGGERS

from .const import (
    DOMAIN,
    DEFAULT_ATTRIBUTION,
)
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Setup Binary Sensors."""
    secspy = hass.data[DOMAIN][entry.entry_id]["secspy"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    nvr = hass.data[DOMAIN][entry.entry_id]["nvr"]
    if not coordinator.data:
        return

    sensors = []
    for camera in coordinator.data:
        sensors.append(
            SecuritySpyBinarySensor(
                secspy, coordinator, nvr, camera, DEVICE_CLASS_MOTION
            )
        )
        _LOGGER.debug(
            "SECURITYSPY MOTION SENSOR CREATED: %s", coordinator.data[camera]["name"]
        )

    async_add_entities(sensors, True)

    return True


class SecuritySpyBinarySensor(SecuritySpyEntity, BinarySensorEntity):
    """A SecuritySpy Camera."""

    def __init__(self, secspy, coordinator, nvr, camera_id, sensor_type):
        """Initialize an Unifi camera."""
        super().__init__(secspy, coordinator, nvr, camera_id, sensor_type)
        self._name = f"{sensor_type.capitalize()} {self._camera_data['name']}"
        self._device_class = sensor_type
        self._data = None

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return False
        # if self._data:
        #     if self._data[self._camera_id]["event_type"] in MOTION_TRIGGERS:
        #         # _LOGGER.debug(
        #         #     f"CAM {self._data[self._camera_id]['name']} MOTION: {self._data[self._camera_id]['is_motion']}"
        #         # )
        #         return bool(self._data[self._camera_id]["is_motion"])
        # else:
        #     return False

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            # ATTR_LAST_TRIP_TIME: self._camera_data["last_motion"],
            # ATTR_EVENT_SCORE: self._camera_data["event_score"],
            # ATTR_EVENT_LENGTH: self._camera_data["event_length"],
        }

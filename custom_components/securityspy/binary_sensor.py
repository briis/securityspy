""" This component provides binary sensors for SecuritySpy."""
import logging
import voluptuous as vol
from datetime import timedelta
import requests

import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import PlatformNotReady
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    CONF_MONITORED_CONDITIONS,
)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from . import (
    NVR_DATA,
    ATTR_LAST_TRIGGER,
    ATTR_TRIGGER_TYPE,
    ATTR_BRAND,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    )

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["securityspy"]

# Update Frequently as we are only reading from Memory
SCAN_INTERVAL = timedelta(seconds=2)

# sensor_type [ description, unit, icon ]
SENSOR_TYPES = {"motion": ["Motion", "motion", "motionDetected"]}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
    }
)

async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an SecuritySpy binary sensor."""
    data = hass.data[NVR_DATA]
    if not data:
        return

    sensors = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        for camera in data.devices:
            sensors.append(SecSpyBinarySensor(data, camera, sensor_type))

    async_add_entities(sensors, True)

class SecSpyBinarySensor(BinarySensorDevice):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, data, camera, sensor_type):
        """Initialize an Arlo sensor."""
        self.data = data
        self._camera_id = camera
        self._camera = self.data.devices[camera]
        self._name = "{0} {1}".format(SENSOR_TYPES[sensor_type][0], self._camera["name"])
        self._unique_id = self._name.lower().replace(" ", "_")
        self._sensor_type = sensor_type
        self._state = False
        self._trigger_type = None
        self._last_trigger = None
        self._class = SENSOR_TYPES.get(self._sensor_type)[1]
        self._attr = SENSOR_TYPES.get(self._sensor_type)[2]

        _LOGGER.debug("Binary Sensor: %s added to Home Assistant", self._name)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state is True

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._class

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = DEFAULT_ATTRIBUTION
        attrs[ATTR_BRAND] = DEFAULT_BRAND
        attrs[ATTR_FRIENDLY_NAME] = self._name
        attrs[ATTR_LAST_TRIGGER] = self._last_trigger
        attrs[ATTR_TRIGGER_TYPE] = self._trigger_type

        return attrs

    def update(self):
        """ Updates Sensor State."""
        self._state = self._camera["motion_on"]
        self._trigger_type = self._camera["motion_trigger_type"]
        self._last_trigger = self._camera["motion_last_trigger"]

""" Constant definitions for SecuritySpy Integration."""

import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from pysecspy.const import (
    RECORDING_TYPE_MOTION,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_OFF,
)

DOMAIN = "securityspy"
UNIQUE_ID = "unique_id"

DEFAULT_PORT = 8000
DEFAULT_ATTRIBUTION = "Powered by SecuritySpy Server"
DEFAULT_BRAND = "@bensoftware"

CONF_RECORDING_MODE = "recording_mode"

ATTR_ONLINE = "online"
ATTR_SENSITIVITY = "motion_sensitivity"
ATTR_IMAGE_WIDTH = "image_width"
ATTR_IMAGE_HEIGHT = "image_height"
ATTR_BRAND = "brand"
ATTR_EVENT_LENGTH = "event_length"
ATTR_EVENT_OBJECT = "event_object"

DEVICE_TYPE_CAMERA = "camera"
DEVICE_TYPE_DOORBELL = "doorbell"
DEVICE_TYPE_MOTION = "motion"
DEVICE_TYPE_NETWORK = "network"

DEVICES_WITH_CAMERA = (DEVICE_TYPE_CAMERA, DEVICE_TYPE_DOORBELL, DEVICE_TYPE_NETWORK)

VALID_RECORDING_MODES = [
    RECORDING_TYPE_MOTION,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_OFF,
]
SERVICE_SET_RECORDING_MODE = "set_recording_mode"
SET_RECORDING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_RECORDING_MODE, default=RECORDING_TYPE_MOTION): vol.In(
            VALID_RECORDING_MODES
        ),
    }
)

SECURITYSPY_PLATFORMS = [
    "camera",
    "binary_sensor",
    "switch",
    "sensor",
]

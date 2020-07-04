""" Constant definitions for SecuritySpy Integration."""

import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_FILENAME,
)
from pysecurityspy import (
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
)

DOMAIN = "securityspy"
UNIQUE_ID = "unique_id"

DEFAULT_PORT = 8000
DEFAULT_ATTRIBUTION = "Powered by SecuritySpy Server"
DEFAULT_BRAND = "@bensoftware"
DEFAULT_SCAN_INTERVAL = 10

CONF_RECORDING_MODE = "recording_mode"

ATTR_ONLINE = "online"
ATTR_SENSITIVITY = "motion_sensitivity"
ATTR_IMAGE_WIDTH = "image_width"
ATTR_IMAGE_HEIGHT = "image_height"

VALID_RECORDING_MODES = [
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_NEVER,
]
SERVICE_SET_RECORDING_MODE = "set_recording_mode"
SET_RECORDING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_RECORDING_MODE, default=RECORDING_MODE_MOTION): vol.In(
            VALID_RECORDING_MODES
        ),
    }
)

SECURITYSPY_PLATFORMS = [
    "camera",
    # "binary_sensor",
]

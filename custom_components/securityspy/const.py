""" Constant definitions for SecuritySpy Integration."""
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_FILENAME,
)
from pysecspy.const import (
    RECORDING_TYPE_ACTION,
    RECORDING_TYPE_MOTION,
    RECORDING_TYPE_CONTINUOUS,
)

DOMAIN = "securityspy"
UNIQUE_ID = "unique_id"

DEFAULT_PORT = 8000
DEFAULT_ATTRIBUTION = "Powered by SecuritySpy Server"
DEFAULT_BRAND = "Ben Software"
MIN_SECSPY_VERSION = "5.3.4"

CONF_MODE = "mode"
CONF_ENABLED = "enabled"
CONF_DISABLE_RTSP = "disable_rtsp"
CONFIG_OPTIONS = [
    CONF_DISABLE_RTSP,
]

ATTR_BRAND = "brand"
ATTR_EVENT_LENGTH = "event_length"
ATTR_EVENT_OBJECT = "event_object"
ATTR_EVENT_SCORE_HUMAN = "event_score_human"
ATTR_EVENT_SCORE_VEHICLE = "event_score_vehicle"
ATTR_PRESET_ID = "preset_id"
ATTR_PTZ_CAPABILITIES = "ptz_capabilities"

DEVICE_CLASS_DETECTION = "securityspy__detection"

DEVICE_TYPE_CAMERA = "camera"
DEVICE_TYPE_DOORBELL = "doorbell"
DEVICE_TYPE_LOCAL = "local"
DEVICE_TYPE_MOTION = "motion"
DEVICE_TYPE_NETWORK = "network"

DEVICES_WITH_CAMERA = (
    DEVICE_TYPE_CAMERA,
    DEVICE_TYPE_DOORBELL,
    DEVICE_TYPE_NETWORK,
    DEVICE_TYPE_LOCAL,
)

VALID_MODES = [
    RECORDING_TYPE_MOTION,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_ACTION,
]
SERVICE_DOWNLOAD_LATEST_MOTION_RECORDING = "download_latest_motion_recording"
SERVICE_ENABLE_SCHEDULE_PRESET = "enable_schedule_preset"
SERVICE_SET_ARM_MODE = "set_arm_mode"
DOWNLOAD_LATEST_MOTION_RECORDING_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_FILENAME): cv.string,
    }
)
ENABLE_SCHEDULE_PRESET_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PRESET_ID): cv.string,
    }
)
SET_ARM_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_MODE): vol.In(VALID_MODES),
        vol.Required(CONF_ENABLED): cv.boolean,
    }
)

SECURITYSPY_PLATFORMS = [
    "camera",
    "binary_sensor",
    "sensor",
    "switch",
    "button",
]

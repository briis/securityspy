""" Constant definitions for SecuritySpy Integration."""

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN = "securityspy"
UNIQUE_ID = "unique_id"

DEFAULT_PORT = 8000
DEFAULT_ATTRIBUTION = "Powered by SecuritySpy Server"
DEFAULT_BRAND = "@bensoftware"
DEFAULT_SCAN_INTERVAL = 10

SECURITYSPY_PLATFORMS = [
    # "camera",
    "binary_sensor",
]

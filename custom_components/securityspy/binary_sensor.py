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
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
from .const import (
    DOMAIN,
    DEFAULT_ATTRIBUTION,
)
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)

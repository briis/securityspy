"""Camera definitions for SecuritySpy."""

import logging
from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_LAST_TRIP_TIME,
)
from pysecurityspy import (
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers import entity_platform

from .const import (
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    ATTR_ONLINE,
    ATTR_SENSITIVITY,
    ATTR_IMAGE_WIDTH,
    ATTR_IMAGE_HEIGHT,
    SERVICE_SET_RECORDING_MODE,
    SET_RECORDING_MODE_SCHEMA,
)
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Discover cameras on a SecuritySpy NVR."""
    secspy = hass.data[DOMAIN][entry.entry_id]["secspy"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    nvr = hass.data[DOMAIN][entry.entry_id]["nvr"]
    if not coordinator.data:
        return

    cameras = [camera for camera in coordinator.data]

    async_add_entities(
        [SecuritySpyCamera(secspy, coordinator, nvr, camera) for camera in cameras]
    )

    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SERVICE_SET_RECORDING_MODE,
        SET_RECORDING_MODE_SCHEMA,
        "async_set_recording_mode",
    )

    return True


class SecuritySpyCamera(SecuritySpyEntity, Camera):
    """A SecuritySpy Camera."""

    def __init__(self, secspy, coordinator, nvr, camera_id):
        """Initialize an Unifi camera."""
        super().__init__(secspy, coordinator, nvr, camera_id, None)
        self._name = self._camera_data["name"]
        self._stream_source = self._camera_data["rtsp_video"]
        self._last_image = None
        self._supported_features = SUPPORT_STREAM if self._stream_source else 0

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    @property
    def supported_features(self):
        """Return supported features for this camera."""
        return self._supported_features

    @property
    def motion_detection_enabled(self):
        """Camera Motion Detection Status."""
        return self._camera_data["recording_mode"]

    @property
    def brand(self):
        """The Cameras Brand."""
        return DEFAULT_BRAND

    @property
    def model(self):
        """Return the camera model."""
        return self._model

    @property
    def is_recording(self):
        """Return true if the device is recording."""
        return (
            True
            if self._camera_data["recording_mode"] != RECORDING_MODE_NEVER
            and self._camera_data["online"]
            else False
        )

    @property
    def device_state_attributes(self):
        """Add additional Attributes to Camera."""

        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_ONLINE: self._camera_data["online"],
            ATTR_SENSITIVITY: self._camera_data["mdsensitivity"],
            ATTR_IMAGE_WIDTH: self._camera_data["image_width"],
            ATTR_IMAGE_HEIGHT: self._camera_data["image_height"],
        }

    async def async_set_recording_mode(self, recording_mode):
        """Set Camera Recording Mode."""
        await self.secspy.set_recording_mode(self._camera_id, recording_mode)

    async def async_update(self):
        """Update the entity.
        Only used by the generic entity update service.
        """
        await self.coordinator.async_request_refresh()

    async def async_enable_motion_detection(self):
        """Enable motion detection in camera."""
        ret = await self.secspy.set_recording_mode(
            self._camera_id, RECORDING_MODE_MOTION
        )
        if not ret:
            return
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self._name)

    async def async_disable_motion_detection(self):
        """Disable motion detection in camera."""
        ret = await self.secspy.set_recording_mode(
            self._camera_id, RECORDING_MODE_NEVER
        )
        if not ret:
            return
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self._name)

    async def async_camera_image(self):
        """ Return the Camera Image. """
        last_image = await self.secspy.get_snapshot_image(self._camera_id)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """ Return the Stream Source. """
        return self._stream_source

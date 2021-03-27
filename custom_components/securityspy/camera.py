"""Camera definitions for SecuritySpy."""

import logging

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LAST_TRIP_TIME
from homeassistant.helpers import entity_platform
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    ATTR_ONLINE,
    RECORDING_TYPE_MOTION,
    SERVICE_SET_MODE,
    SET_MODE_SCHEMA,
)
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Discover cameras on a SecuritySpy NVR."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    cameras = []
    for camera_id in secspy_data.data:
        cameras.append(
            SecuritySpyCamera(secspy_object, secspy_data, server_info, camera_id)
        )
        _LOGGER.debug("SECURITYSPY CAMERA CREATED: %s", camera_id)

    async_add_entities(cameras)

    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SERVICE_SET_MODE,
        SET_MODE_SCHEMA,
        "async_set_mode",
    )

    return True


class SecuritySpyCamera(SecuritySpyEntity, Camera):
    """A SecuritySpy Camera."""

    def __init__(self, secspy_object, secspy_data, server_info, camera_id):
        """Initialize an SecuritySpy camera."""
        super().__init__(secspy_object, secspy_data, server_info, camera_id, None)
        self._name = self._device_data["name"]
        self._stream_source = self._device_data["live_stream"]
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
        return self._device_data["recording_mode_m"]

    @property
    def brand(self):
        """Return the Cameras Brand."""
        return DEFAULT_BRAND

    @property
    def model(self):
        """Return the camera model."""
        return self._model

    @property
    def is_recording(self):
        """Return true if the device is recording."""
        return bool(
            (
                self._device_data["recording_mode_c"]
                or self._device_data["recording_mode_m"]
            )
            and self._device_data["online"]
        )

    @property
    def device_state_attributes(self):
        """Add additional Attributes to Camera."""
        last_trip_time = self._device_data["last_motion"]

        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_ONLINE: self._device_data["online"],
            ATTR_LAST_TRIP_TIME: last_trip_time,
        }

    async def async_set_mode(self, mode, enabled):
        """Set Camera Mode."""
        await self.secspy.set_camera_recording(self._device_id, mode, enabled)

    async def async_enable_motion_detection(self):
        """Enable motion detection in camera."""
        if not await self.secspy.set_camera_recording(
            self._device_id, RECORDING_TYPE_MOTION, True
        ):
            return
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self._name)

    async def async_disable_motion_detection(self):
        """Disable motion detection in camera."""
        if not await self.secspy.set_camera_recording(
            self._device_id, RECORDING_TYPE_MOTION, False
        ):
            return
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self._name)

    async def async_camera_image(self):
        """Return the Camera Image."""
        last_image = await self.secspy.get_snapshot_image(self._device_id)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """Return the Stream Source."""
        return self._stream_source

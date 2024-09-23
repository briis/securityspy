"""Camera definitions for SecuritySpy."""
from __future__ import annotations

import logging

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LAST_TRIP_TIME
from homeassistant.helpers import entity_platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DEFAULT_BRAND,
    DOWNLOAD_LATEST_MOTION_RECORDING_SCHEMA,
    ATTR_PRESET_ID,
    ATTR_PTZ_CAPABILITIES,
    RECORDING_TYPE_MOTION,
    SERVICE_SET_ARM_MODE,
    SERVICE_DOWNLOAD_LATEST_MOTION_RECORDING,
    SET_ARM_MODE_SCHEMA,
)
from .entity import SecuritySpyEntity

CONF_RTSP_TRANSPORT = "rtsp_transport"
FFMPEG_OPTION_MAP = {CONF_RTSP_TRANSPORT: "rtsp_transport"}
ALLOWED_RTSP_TRANSPORT_PROTOCOLS = {"tcp", "udp", "udp_multicast", "http"}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Discover cameras on a SecuritySpy NVR."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    disable_stream = entry_data["disable_stream"]

    if not secspy_data.data:
        return

    cameras = []
    for camera_id in secspy_data.data:
        cameras.append(
            SecuritySpyCamera(
                secspy_object, secspy_data, server_info, camera_id, disable_stream
            )
        )
        _LOGGER.debug("Adding Camera Id: %s", camera_id)

    async_add_entities(cameras)

    platform = entity_platform.async_get_current_platform()

    _LOGGER.debug("Creating Service: Set Arm Mode")
    platform.async_register_entity_service(
        SERVICE_SET_ARM_MODE,
        SET_ARM_MODE_SCHEMA,
        "async_set_arm_mode",
    )

    _LOGGER.debug("Creating Service: Download Latest Recording")
    platform.async_register_entity_service(
        SERVICE_DOWNLOAD_LATEST_MOTION_RECORDING,
        DOWNLOAD_LATEST_MOTION_RECORDING_SCHEMA,
        "async_download_latest_motion_recording",
    )


class SecuritySpyCamera(SecuritySpyEntity, Camera):
    """A SecuritySpy Camera."""

    def __init__(
        self, secspy_object, secspy_data, server_info, camera_id, disable_stream
    ):
        """Initialize an SecuritySpy camera."""
        super().__init__(secspy_object, secspy_data, server_info, camera_id, None)
        self._name = self._device_data["name"]
        self._stream_source = (
            None if disable_stream else self._device_data["live_stream"]
        )
        self._last_image: bytes | None = None
        if self._stream_source:
            self._attr_supported_features = CameraEntityFeature.STREAM
        else:
            self._attr_supported_features = CameraEntityFeature(0)
        self.stream_options[FFMPEG_OPTION_MAP[CONF_RTSP_TRANSPORT]] = "tcp"

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

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
            and self._device_data["event_online"]
        )

    @property
    def extra_state_attributes(self):
        """Add additional Attributes to Camera."""
        last_trip_time = self._device_data["last_motion"]

        return {
            **super().extra_state_attributes,
            ATTR_LAST_TRIP_TIME: last_trip_time,
            ATTR_PRESET_ID: self._schedule_presets,
            ATTR_PTZ_CAPABILITIES: self._device_data["ptz_capabilities"],
        }

    async def async_set_arm_mode(self, mode, enabled):
        """Set Arming Mode."""
        _LOGGER.debug("Setting Arm Mode for %s to %s", mode, enabled)
        await self.secspy.set_arm_mode(self._device_id, mode, enabled)

    async def async_download_latest_motion_recording(self, filename):
        """Download and save latest motion recording."""

        if not self.hass.config.is_allowed_path(filename):
            _LOGGER.debug(self.hass.config.path())
            _LOGGER.error("Can't write %s, no access to path!", filename)
            return

        video = await self.secspy.get_latest_motion_recording(self._device_id)
        if video is None:
            _LOGGER.error("Last recording not found for Camera %s", self.name)
            return

        _LOGGER.debug("Saving recording in %s", filename)
        try:
            await self.hass.async_add_executor_job(_write_file, filename, video)
        except OSError as err:
            _LOGGER.error("Can't write video to file: %s", err)

    async def async_enable_motion_detection(self):
        """Enable motion detection in camera."""
        if not await self.secspy.set_arm_mode(
            self._device_id, RECORDING_TYPE_MOTION, True
        ):
            return
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self._name)

    async def async_disable_motion_detection(self):
        """Disable motion detection in camera."""
        if not await self.secspy.set_arm_mode(
            self._device_id, RECORDING_TYPE_MOTION, False
        ):
            return
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self._name)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return the Camera Image."""
        if self._device_data["event_online"]:
            last_image = await self.secspy.get_snapshot_image(
                self._device_id, width, height
            )
            self._last_image = last_image
            return self._last_image

    async def stream_source(self):
        """Return the Stream Source."""
        return self._stream_source


def _write_file(to_file, content):
    """Executor helper to write file."""
    with open(to_file, "wb") as _file:
        _file.write(content)
        _LOGGER.debug("File written to %s", to_file)


""" This component provides Switches for SecuritySpy."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from .entity import SecuritySpyEntity
from .const import (
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    ATTR_BRAND,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_MOTION,
    RECORDING_TYPE_OFF,
)

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = {
    "record_motion": ["Record Motion", "motion-sensor", "record_motion"],
    "record_always": ["Record Always", "video", "record_always"],
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A SecsuritySpy Switch."""
    secspy = hass.data[DOMAIN][entry.entry_id]["secspy"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    nvr = hass.data[DOMAIN][entry.entry_id]["nvr"]
    if not coordinator.data:
        return

    switches = []
    for switch in SWITCH_TYPES:
        for camera in coordinator.data:
            switches.append(
                SecuritySpySwitch(
                    secspy,
                    coordinator,
                    nvr,
                    camera,
                    switch,
                )
            )
            _LOGGER.debug("SECURITYSPY SWITCH CREATED: %s", switch)

    async_add_entities(switches, True)

    return True


class SecuritySpySwitch(SecuritySpyEntity, SwitchEntity):
    """A SecuritySpy Switch."""

    def __init__(self, secspy, coordinator, nvr, camera_id, switch):
        """Initialize a SecuritySpy Switch."""
        super().__init__(secspy, coordinator, nvr, camera_id, switch)
        self._name = f"{SWITCH_TYPES[switch][0]} {self._camera_data['name']}"
        self._icon = f"mdi:{SWITCH_TYPES[switch][1]}"
        self._switch_type = SWITCH_TYPES[switch][2]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        if self._switch_type == "record_motion":
            enabled = (
                True
                if self._camera_data["recording_mode"] == RECORDING_TYPE_MOTION
                else False
            )
        else:
            enabled = (
                True
                if self._camera_data["recording_mode"] == RECORDING_TYPE_CONTINUOUS
                else False
            )
        return enabled

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_BRAND: DEFAULT_BRAND,
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self._switch_type == "record_motion":
            _LOGGER.debug("Turning on Motion Detection")
            await self.secspy.set_recording_mode(self._camera_id, RECORDING_TYPE_MOTION)
        else:
            _LOGGER.debug("Turning on Constant Recording")
            await self.secspy.set_recording_mode(
                self._camera_id, RECORDING_TYPE_CONTINUOUS
            )

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turning off Recording")
        await self.secspy.set_recording_mode(self._camera_id, RECORDING_TYPE_OFF)

        await self.coordinator.async_request_refresh()

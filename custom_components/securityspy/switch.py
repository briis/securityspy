""" This component provides Switches for SecuritySpy."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    ATTR_BRAND,
    RECORDING_TYPE_ACTION,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_MOTION,
)
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)

_SWITCH_NAME = 0
_SWITCH_ICON = 1
_SWITCH_TYPE = 2
_SWITCH_REQUIRES = 3

SWITCH_TYPES = {
    "enable_action": [
        "Actions",
        "script-text-play",
        RECORDING_TYPE_ACTION,
        None,
    ],
    "record_motion": [
        "Record Motion",
        "motion-sensor",
        RECORDING_TYPE_MOTION,
        None,
    ],
    "record_continuous": [
        "Record Continuous",
        "video",
        RECORDING_TYPE_CONTINUOUS,
        None,
    ],
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A SecsuritySpy Switch."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    switches = []
    for switch, switch_type in SWITCH_TYPES.items():
        required_field = switch_type[_SWITCH_REQUIRES]

        for device_id in secspy_data.data:
            # Only Add Switches if Device supports it.
            if required_field and not secspy_data.data[device_id].get(required_field):
                continue

            switches.append(
                SecuritySpySwitch(
                    secspy_object, secspy_data, server_info, device_id, switch
                )
            )
            _LOGGER.debug("SECURITYSPY SWITCH CREATED: %s", switch)

    async_add_entities(switches, True)

    return True


class SecuritySpySwitch(SecuritySpyEntity, SwitchEntity):
    """A SecuritySpy Switch."""

    def __init__(self, secspy_object, secspy_data, server_info, device_id, switch):
        """Initialize a SecuritySpy Switch."""
        super().__init__(secspy_object, secspy_data, server_info, device_id, switch)
        switch_type = SWITCH_TYPES[switch]
        self._name = f"{switch_type[_SWITCH_NAME]} {self._device_data['name']}"
        self._icon = f"mdi:{switch_type[_SWITCH_ICON]}"
        self._switch_type = switch_type[_SWITCH_TYPE]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        if self._switch_type == RECORDING_TYPE_ACTION:
            return self._device_data["recording_mode_a"]
        if self._switch_type == RECORDING_TYPE_MOTION:
            return self._device_data["recording_mode_m"]
        if self._switch_type == RECORDING_TYPE_CONTINUOUS:
            return self._device_data["recording_mode_c"]

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
        if self._switch_type == RECORDING_TYPE_ACTION:
            _LOGGER.debug("Turning on Actions")
            await self.secspy.set_arm_mode(self._device_id, RECORDING_TYPE_ACTION, True)
        if self._switch_type == RECORDING_TYPE_MOTION:
            _LOGGER.debug("Turning on Motion Recording")
            await self.secspy.set_arm_mode(self._device_id, RECORDING_TYPE_MOTION, True)
        if self._switch_type == RECORDING_TYPE_CONTINUOUS:
            _LOGGER.debug("Turning on Continuous Recording")
            await self.secspy.set_arm_mode(
                self._device_id, RECORDING_TYPE_CONTINUOUS, True
            )

        await self.secspy_data.async_refresh(force_camera_update=True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turning off Action or Recording")
        await self.secspy.set_arm_mode(self._device_id, self._switch_type, False)

        await self.secspy_data.async_refresh(force_camera_update=True)

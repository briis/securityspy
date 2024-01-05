"""This component provides Switches for SecuritySpy."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    RECORDING_TYPE_ACTION,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_MOTION,
)
from .entity import SecuritySpyEntity
from .models import SecSpyRequiredKeysMixin


@dataclass(frozen=True, kw_only=True)
class SecSpyBinarySwitchDescription(SecSpyRequiredKeysMixin, SwitchEntityDescription):
    """Describes SecuritySpy Switch entity."""


SWITCH_ENTITIES: tuple[SecSpyBinarySwitchDescription, ...] = (
    SecSpyBinarySwitchDescription(
        key="enable_action",
        name="Actions",
        icon="mdi:script-text-play",
        device_type=RECORDING_TYPE_ACTION,
    ),
    SecSpyBinarySwitchDescription(
        key="record_motion",
        name="Record Motion",
        icon="mdi:motion-sensor",
        device_type=RECORDING_TYPE_MOTION,
    ),
    SecSpyBinarySwitchDescription(
        key="record_continuous",
        name="Record Continuous",
        icon="mdi:video",
        device_type=RECORDING_TYPE_CONTINUOUS,
    ),
)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """SecuritySpy Switch Platform."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    switches = []
    for description in SWITCH_ENTITIES:
        for device_id in secspy_data.data:
            device_data = secspy_data.data[device_id]
            switches.append(
                SecuritySpySwitch(
                    secspy_object, secspy_data, server_info, device_id, description
                )
            )
            _LOGGER.debug(
                "Adding switch entity %s for Camera %s",
                description.name,
                device_data["name"],
            )

    async_add_entities(switches, True)


class SecuritySpySwitch(SecuritySpyEntity, SwitchEntity):
    """A SecuritySpy Switch."""

    def __init__(
        self,
        secspy_object,
        secspy_data,
        server_info,
        device_id,
        description: SecSpyBinarySwitchDescription,
    ):
        """Initialize a SecuritySpy Switch."""
        super().__init__(
            secspy_object, secspy_data, server_info, device_id, description.key
        )
        self._description = description
        self._attr_name = f"{self._device_data['name']} {self._description.name}"
        self._attr_icon = self._description.icon
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def is_on(self):
        """Return true if device is on."""
        if self._description.device_type == RECORDING_TYPE_ACTION:
            return self._device_data["recording_mode_a"]
        if self._description.device_type == RECORDING_TYPE_MOTION:
            return self._device_data["recording_mode_m"]
        if self._description.device_type == RECORDING_TYPE_CONTINUOUS:
            return self._device_data["recording_mode_c"]

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self._description.device_type == RECORDING_TYPE_ACTION:
            _LOGGER.debug("Turning on Actions")
            await self.secspy.set_arm_mode(self._device_id, RECORDING_TYPE_ACTION, True)
        if self._description.device_type == RECORDING_TYPE_MOTION:
            _LOGGER.debug("Turning on Motion Recording")
            await self.secspy.set_arm_mode(self._device_id, RECORDING_TYPE_MOTION, True)
        if self._description.device_type == RECORDING_TYPE_CONTINUOUS:
            _LOGGER.debug("Turning on Continuous Recording")
            await self.secspy.set_arm_mode(
                self._device_id, RECORDING_TYPE_CONTINUOUS, True
            )

        await self.secspy_data.async_refresh(force_camera_update=True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turning off Action or Recording")
        await self.secspy.set_arm_mode(
            self._device_id, self._description.device_type, False
        )

        await self.secspy_data.async_refresh(force_camera_update=True)

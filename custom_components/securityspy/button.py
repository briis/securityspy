"""Support for SecuritySpy NVR."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)

_PTZ_STANDARDS = {
    "Left": 1,
    "Right": 2,
    "Up": 3,
    "Down": 4,
    "Zoom In": 5,
    "Zoom Out": 6,
    "Stop": 99,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """SecuritySpy Button Platform."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    sensors = []
    for device_id in secspy_data.data:
        device_data = secspy_data.data[device_id]
        if int(device_data["ptz_capabilities"]) > 0:
            preset_index = 12
            for preset in device_data["ptz_presets"]:
                sensors.append(
                    SecuritySpyButtonEntity(
                        secspy_object,
                        secspy_data,
                        server_info,
                        device_id,
                        preset,
                        preset_index,
                    )
                )
                preset_index += 1
                _LOGGER.debug(
                    "Adding Button Entity %s to Camera %s", preset, device_data["name"]
                )
            # Add Standrad Buttons to each ptz capable Camera
            for name, std_preset in _PTZ_STANDARDS.items():
                sensors.append(
                    SecuritySpyButtonEntity(
                        secspy_object,
                        secspy_data,
                        server_info,
                        device_id,
                        name,
                        std_preset,
                    )
                )

    async_add_entities(sensors)

    return True


class SecuritySpyButtonEntity(SecuritySpyEntity, ButtonEntity):
    """A SecuritySpy Button entity."""

    def __init__(
        self,
        secspy_object,
        secspy_data,
        server_info,
        device_id,
        preset_id,
        preset_index,
    ):
        """Initialize the Button entity."""
        super().__init__(secspy_object, secspy_data, server_info, device_id, preset_id)
        self._preset_id = preset_id
        self._preset_index = preset_index
        self._attr_name = f"{self._device_data['name']} {preset_id.capitalize()}"
        self._attr_device_class = ButtonDeviceClass.UPDATE

    @callback
    async def async_press(self) -> None:
        """Press the button."""

        _LOGGER.debug(
            "Activating PTZ command %s for Camera %s", self._preset_id, self._device_id
        )
        _preset_speed = 80
        if self._preset_index < 12:
            _preset_speed = 40
        await self.secspy.set_ptz_preset(
            self._device_id, self._preset_index, _preset_speed
        )

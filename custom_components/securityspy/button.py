"""Support for SecuritySpy NVR."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .entity import SecuritySpyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Setup Binary Sensors."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    sensors = []
    for device_id in secspy_data.data:
        device_data = secspy_data.data[device_id]
        if device_data["ptz_capabilities"] > 0:
            for preset in device_data["ptz_presets"]:
                sensors.append(
                    SecuritySpyButtonEntity(
                        secspy_object, secspy_data, server_info, device_id, preset
                    )
                )
                _LOGGER.debug(
                    "Adding Button Entity %s to Camera %s", preset, device_data["name"]
                )

    async_add_entities(sensors)

    return True


class SecuritySpyButtonEntity(SecuritySpyEntity, ButtonEntity):
    """A SecuritySpy Button entity."""

    def __init__(self, secspy_object, secspy_data, server_info, device_id, preset_id):
        """Initialize the Button entity."""
        super().__init__(secspy_object, secspy_data, server_info, device_id, preset_id)
        self._preset_id = preset_id
        self._attr_name = f"{self._device_data['name']} {preset_id.capitalize()}"
        self._attr_device_class = ButtonDeviceClass.UPDATE

    @callback
    async def async_press(self) -> None:
        """Press the button."""

        _LOGGER.debug(
            "Activating PTZ Preset %s for Camera %s", self._preset_id, self._device_id
        )
        await self.secspy.set_ptz_preset(self._device_id, self._preset_id)

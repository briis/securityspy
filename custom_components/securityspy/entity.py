"""Shared Entity definition for SecurotySpy Integration."""
from __future__ import annotations

import logging

from homeassistant.const import ATTR_ATTRIBUTION
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import Entity, DeviceInfo

from .const import (
    ATTR_BRAND,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DOMAIN,
)
from .data import SecuritySpyData

_LOGGER = logging.getLogger(__name__)


class SecuritySpyEntity(Entity):
    """Base class for SecuritySpy entities."""

    def __init__(
        self,
        secspy,
        secspy_data: SecuritySpyData,
        server_info,
        device_id,
        sensor_type,
    ):
        """Initialize the entity."""
        super().__init__()
        self.secspy = secspy
        self.secspy_data = secspy_data
        self._device_id = device_id
        self._sensor_type = sensor_type

        self._device_data = self.secspy_data.data[self._device_id]
        self._device_name = self._device_data["name"]
        self._mac = f"{self._device_data['ip_address']}_{self._device_id}"
        self._firmware_version = server_info["server_version"]
        self._server_id = server_info["server_id"]
        self._schedule_presets = server_info["schedule_presets"]
        self._device_type = self._device_data["type"]
        self._model = self._device_data["model"]
        self._server_ip = server_info["server_ip_address"]
        self._server_port = server_info["server_port"]

        self._attr_available = self.secspy_data.last_update_success
        if self._sensor_type is None:
            self._attr_unique_id = f"{self._device_id}_{self._server_id}"
        else:
            self._attr_unique_id = (
                f"{self._sensor_type}_{self._server_id}_{self._device_id}"
            )
        self._attr_device_info = DeviceInfo(
            connections={(dr.CONNECTION_NETWORK_MAC, self._mac)},
            name=self._device_name,
            manufacturer=DEFAULT_BRAND,
            model=self._model,
            sw_version=self._firmware_version,
            via_device=(DOMAIN, self._server_id),
            configuration_url=f"http://{self._server_ip}:{self._server_port}/camerasettings?cameraNum={self._device_id}",
        )

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_BRAND: DEFAULT_BRAND,
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.secspy_data.async_subscribe_device_id(
                self._device_id, self.async_write_ha_state
            )
        )

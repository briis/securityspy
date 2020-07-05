from homeassistant.helpers.entity import Entity
import homeassistant.helpers.device_registry as dr
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_BRAND


class SecuritySpyEntity(Entity):
    """Base class for SecuritySpy entities."""

    def __init__(self, secspy, coordinator, nvr, camera_id, sensor_type):
        """Initialize the entity."""
        super().__init__()
        self.secspy = secspy
        self.nvr = nvr
        self.coordinator = coordinator
        self._camera_id = camera_id
        self._sensor_type = sensor_type

        self._camera_data = self.coordinator.data[self._camera_id]
        self._camera_name = self._camera_data["name"]
        self._mac = f"{self._camera_data['address']}_{self._camera_id}"
        self._server_id = self.nvr["host"]
        self._device_type = self._camera_data["camera_type"]
        self._model = self._camera_data["camera_model"]
        if self._sensor_type is None:
            self._unique_id = f"{self._camera_id}_{self._mac}"
        else:
            self._unique_id = f"{self._sensor_type}_{self._mac}"

    @property
    def should_poll(self):
        """Poll Cameras to update attributes."""
        return False

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._server_id)},
            "name": self._camera_name,
            "manufacturer": DEFAULT_BRAND,
            "model": self._device_type,
            "via_device": (DOMAIN, self._server_id),
        }

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

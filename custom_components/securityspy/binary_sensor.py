"""This component provides binary sensors for SecuritySpy."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_LAST_TRIP_TIME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_EVENT_LENGTH,
    ATTR_EVENT_OBJECT,
    ATTR_EVENT_SCORE_ANIMAL,
    ATTR_EVENT_SCORE_HUMAN,
    ATTR_EVENT_SCORE_VEHICLE,
    DOMAIN,
)
from .entity import SecuritySpyEntity
from .models import SecSpyRequiredKeysMixin


@dataclass(frozen=True, kw_only=True)
class SecSpyBinaryEntityDescription(
    SecSpyRequiredKeysMixin, BinarySensorEntityDescription
):
    """Describes SecuritySpy Binary Sensor entity."""


BINARY_SENSORS: tuple[SecSpyBinaryEntityDescription, ...] = (
    SecSpyBinaryEntityDescription(
        key="motion",
        name="Motion",
        device_class=BinarySensorDeviceClass.MOTION,
        trigger_field="event_on",
    ),
    SecSpyBinaryEntityDescription(
        key="online",
        icon="mdi:access-point-network",
        name="Online",
        trigger_field="event_online",
    ),
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """SecuritySpy Binary Sensor Platform."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    sensors = []
    for device_id in secspy_data.data:
        device_data = secspy_data.data[device_id]
        for description in BINARY_SENSORS:
            sensors.append(
                SecuritySpyBinarySensor(
                    secspy_object,
                    secspy_data,
                    server_info,
                    device_id,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding binary sensor entity %s for Camera %s",
                description.name,
                device_data["name"],
            )

    async_add_entities(sensors)


class SecuritySpyBinarySensor(SecuritySpyEntity, BinarySensorEntity):
    """A SecuritySpy Binary Sensor."""

    def __init__(
        self,
        secspy_object,
        secspy_data,
        server_info,
        device_id,
        description: SecSpyBinaryEntityDescription,
    ):
        """Initialize the Binary Sensor."""
        super().__init__(
            secspy_object, secspy_data, server_info, device_id, description.key
        )
        self._description = description
        self._attr_name = f"{self._device_data['name']} {self._description.name}"
        self._attr_device_class = self._description.device_class
        self._attr_icon = self._description.icon

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._device_data[self._description.trigger_field]

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        if self._description.device_class == BinarySensorDeviceClass.MOTION:
            return {
                **super().extra_state_attributes,
                ATTR_LAST_TRIP_TIME: self._device_data["last_motion"],
                ATTR_EVENT_LENGTH: self._device_data["event_length"],
                ATTR_EVENT_OBJECT: self._device_data["event_object"],
                ATTR_EVENT_SCORE_ANIMAL: self._device_data[ATTR_EVENT_SCORE_ANIMAL],
                ATTR_EVENT_SCORE_HUMAN: self._device_data[ATTR_EVENT_SCORE_HUMAN],
                ATTR_EVENT_SCORE_VEHICLE: self._device_data[ATTR_EVENT_SCORE_VEHICLE],
            }
        return {
            **super().extra_state_attributes,
        }

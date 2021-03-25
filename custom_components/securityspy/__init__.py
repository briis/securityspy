"""SecuritySpy Platform."""

import asyncio
from datetime import timedelta
import logging

from aiohttp.client_exceptions import ServerDisconnectedError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ID,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from pysecspy.errors import InvalidCredentials, RequestError, ResultError
from pysecspy.secspy_server import SecSpyServer
from pysecspy.const import SERVER_ID

from .const import (
    DEFAULT_BRAND,
    DOMAIN,
    SECURITYSPY_PLATFORMS,
)
from .data import SecuritySpyData

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Set up the SecuritySpy components."""

    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Set up the SecuritySpy config entries."""

    session = async_create_clientsession(hass)
    securityspy = SecSpyServer(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = securityspy
    _LOGGER.debug("Connect to SecuritySpy")

    secspy_data = SecuritySpyData(hass, securityspy, timedelta(seconds=2))

    try:
        server_info = await securityspy.get_server_information()
    except InvalidCredentials as unauthex:
        _LOGGER.error("Could not authorize against SecuritySpy. Error: %s.", unauthex)
        return
    except (RequestError, ServerDisconnectedError) as notreadyerror:
        raise ConfigEntryNotReady from notreadyerror

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=server_info[SERVER_ID])

    await secspy_data.async_setup()
    if not secspy_data.last_update_success:
        raise ConfigEntryNotReady

    update_listener = entry.add_update_listener(_async_options_updated)

    hass.data[DOMAIN][entry.entry_id] = {
        "secspy_data": secspy_data,
        "nvr": securityspy,
        "server_info": server_info,
        "update_listener": update_listener,
    }

    await _async_get_or_create_nvr_device_in_registry(hass, entry, server_info)

    for platform in SECURITYSPY_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def _async_get_or_create_nvr_device_in_registry(
    hass: HomeAssistantType, entry: ConfigEntry, nvr
) -> None:
    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, nvr["server_id"])},
        identifiers={(DOMAIN, nvr["server_id"])},
        manufacturer=DEFAULT_BRAND,
        name=entry.data[CONF_ID],
        model="No Model",
        sw_version=nvr["server_version"],
    )


async def _async_options_updated(hass: HomeAssistantType, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Unload Unifi Protect config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in SECURITYSPY_PLATFORMS
            ]
        )
    )

    if unload_ok:
        entry_data = hass.data[DOMAIN][entry.entry_id]
        entry_data["update_listener"]()
        await entry_data["secspy_data"].async_stop()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

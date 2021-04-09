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
    CONF_DISABLE_RTSP,
    DEFAULT_BRAND,
    DOMAIN,
    SECURITYSPY_PLATFORMS,
    SERVICE_ENABLE_SCHEDULE_PRESET,
    ENABLE_SCHEDULE_PRESET_SCHEMA,
)
from .data import SecuritySpyData

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Set up the SecuritySpy components."""

    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Set up the SecuritySpy config entries."""

    if not entry.options:
        hass.config_entries.async_update_entry(
            entry,
            options={
                CONF_HOST: entry.data.get(CONF_HOST),
                CONF_PORT: entry.data.get(CONF_PORT),
                CONF_USERNAME: entry.data.get(CONF_USERNAME),
                CONF_PASSWORD: entry.data.get(CONF_PASSWORD),
                CONF_DISABLE_RTSP: entry.data.get(CONF_DISABLE_RTSP, False),
            },
        )

    session = async_create_clientsession(hass)
    securityspyserver = SecSpyServer(
        session,
        entry.options[CONF_HOST],
        entry.options[CONF_PORT],
        entry.options[CONF_USERNAME],
        entry.options[CONF_PASSWORD],
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = securityspyserver
    _LOGGER.debug("Connect to SecuritySpy")

    # secspy_data = SecuritySpyData(hass, securityspyserver, timedelta(seconds=2))
    secspy_data = SecuritySpyData(hass, securityspyserver)

    try:
        server_info = await securityspyserver.get_server_information()
    except InvalidCredentials as unauthex:
        _LOGGER.error("Could not authorize against SecuritySpy. Error: %s.", unauthex)
        return False
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
        "nvr": securityspyserver,
        "server_info": server_info,
        "update_listener": update_listener,
        "disable_stream": entry.options[CONF_DISABLE_RTSP],
    }

    await _async_get_or_create_nvr_device_in_registry(hass, entry, server_info)

    for platform in SECURITYSPY_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    async def async_enable_schedule_preset(service_entries):
        """Call Enable Schedule Preset Handler."""
        await async_handle_enable_schedule_preset(hass, entry, service_entries)

    hass.services.async_register(
        DOMAIN,
        SERVICE_ENABLE_SCHEDULE_PRESET,
        async_enable_schedule_preset,
        schema=ENABLE_SCHEDULE_PRESET_SCHEMA,
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
        model="Max OSX Computer",
        sw_version=nvr["server_version"],
    )


async def async_handle_enable_schedule_preset(hass, entry, service_entries):
    """Enable Schedule Preset."""

    _LOGGER.debug("Setting Schedule Preset ID: %s", service_entries.data["preset_id"])
    preset_id = service_entries.data["preset_id"]
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy = entry_data["nvr"]

    await secspy.enable_schedule_preset(preset_id)


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
        hass.services.async_remove(DOMAIN, SERVICE_ENABLE_SCHEDULE_PRESET)
        entry_data = hass.data[DOMAIN][entry.entry_id]
        entry_data["update_listener"]()
        await entry_data["secspy_data"].async_stop()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

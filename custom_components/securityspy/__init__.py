"""SecuritySpy Platform."""
from __future__ import annotations

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
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.device_registry as dr
from pysecspy.errors import InvalidCredentials, RequestError
from pysecspy.secspy_server import SecSpyServer
from pysecspy.const import SERVER_ID

from .const import (
    CONF_DISABLE_RTSP,
    CONF_MIN_SCORE,
    CONFIG_OPTIONS,
    DEFAULT_BRAND,
    DEFAULT_MIN_SCORE,
    DOMAIN,
    SECURITYSPY_PLATFORMS,
    SERVICE_ENABLE_SCHEDULE_PRESET,
    ENABLE_SCHEDULE_PRESET_SCHEMA,
    MIN_SECSPY_VERSION,
)
from .data import SecuritySpyData

_LOGGER = logging.getLogger(__name__)


@callback
def _async_import_options_from_data_if_missing(hass: HomeAssistant, entry: ConfigEntry):
    options = dict(entry.options)
    data = dict(entry.data)
    modified = False
    for importable_option in CONFIG_OPTIONS:
        if importable_option not in entry.options and importable_option in entry.data:
            options[importable_option] = entry.data[importable_option]
            del data[importable_option]
            modified = True

    if modified:
        hass.config_entries.async_update_entry(entry, data=data, options=options)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the SecuritySpy config entries."""
    _async_import_options_from_data_if_missing(hass, entry)

    session = async_create_clientsession(hass)
    securityspyserver = SecSpyServer(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.options.get(CONF_MIN_SCORE, DEFAULT_MIN_SCORE),
    )

    secspy_data = SecuritySpyData(hass, securityspyserver)

    try:
        server_info = await securityspyserver.get_server_information()
    except InvalidCredentials as unauthex:
        _LOGGER.error("Could not authorize against SecuritySpy. Error: %s.", unauthex)
        return False
    except (RequestError, ServerDisconnectedError) as notreadyerror:
        raise ConfigEntryNotReady from notreadyerror

    if server_info["server_version"] < MIN_SECSPY_VERSION:
        _LOGGER.error(
            "This version of SecuritySpy is too old. Please upgrade to minimum V%s and try again.",
            MIN_SECSPY_VERSION,
        )
        return False

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=server_info[SERVER_ID])

    await secspy_data.async_setup()
    if not secspy_data.last_update_success:
        raise ConfigEntryNotReady

    update_listener = entry.add_update_listener(_async_options_updated)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = securityspyserver
    hass.data[DOMAIN][entry.entry_id] = {
        "secspy_data": secspy_data,
        "nvr": securityspyserver,
        "server_info": server_info,
        "update_listener": update_listener,
        "disable_stream": entry.options.get(CONF_DISABLE_RTSP, False),
    }

    await _async_get_or_create_nvr_device_in_registry(hass, entry, server_info)
    await hass.config_entries.async_forward_entry_setups(entry, SECURITYSPY_PLATFORMS)

    # hass.config_entries.async_setup_platforms(entry, SECURITYSPY_PLATFORMS)

    async def async_enable_schedule_preset(service_entries):
        """Call Enable Schedule Preset Handler."""
        await async_handle_enable_schedule_preset(hass, entry, service_entries)

    _LOGGER.debug("Creating Service: Enable Schedule Preset")
    hass.services.async_register(
        DOMAIN,
        SERVICE_ENABLE_SCHEDULE_PRESET,
        async_enable_schedule_preset,
        schema=ENABLE_SCHEDULE_PRESET_SCHEMA,
    )

    return True


async def _async_get_or_create_nvr_device_in_registry(
    hass: HomeAssistant, entry: ConfigEntry, nvr
) -> None:
    device_registry = dr.async_get(hass)
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


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SecuritySpy config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, SECURITYSPY_PLATFORMS
    )

    if unload_ok:
        hass.services.async_remove(DOMAIN, SERVICE_ENABLE_SCHEDULE_PRESET)
        entry_data = hass.data[DOMAIN][entry.entry_id]
        await entry_data["secspy_data"].async_stop()
        entry_data["update_listener"]()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

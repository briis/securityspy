"""
    SecuritySpy Integration
    Author: Bjarne Riis
    Github: @briis
"""
import asyncio
from datetime import timedelta
import logging

from pysecurityspy import (
    SecuritySpyServer,
    SecuritySpyEvents,
    InvalidCredentials,
    RequestError,
    ResultError,
)
from aiohttp.client_exceptions import ServerDisconnectedError

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import homeassistant.helpers.device_registry as dr

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_ID,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)

from .const import (
    DEFAULT_BRAND,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SECURITYSPY_PLATFORMS,
)

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
                CONF_SCAN_INTERVAL: entry.data.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            },
        )

    session = async_create_clientsession(hass)
    securityspy = SecuritySpyServer(
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        False,
        session,
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = securityspy
    _LOGGER.debug("Connect to SecuritySpy")

    update_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=securityspy.async_get_cameras,
        update_interval=timedelta(seconds=update_interval),
    )

    try:
        server_info = await securityspy.get_server_information()
    except InvalidCredentials:
        _LOGGER.error(
            "Could not Authorize against SecuritySpy. Please reinstall the Integration."
        )
        return
    except (RequestError, ServerDisconnectedError):
        raise ConfigEntryNotReady

    await coordinator.async_refresh()
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "secspy": securityspy,
    }

    return True

""" 
    SecuritySpy Integration 
    Author: Bjarne Riis 
    Github: @briis
"""

from datetime import timedelta
import logging
import voluptuous as vol
import requests

from . import securityspy_server as nvr

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_FILENAME,
    CONF_SCAN_INTERVAL,
    ATTR_ENTITY_ID,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity

from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

_LOGGER = logging.getLogger(__name__)

ATTR_CAMERA_ID = "camera_id"
ATTR_ONLINE = "online"

CONF_RECORDING_MODE = "recording_mode"

DEFAULT_ATTRIBUTION = "Data provided by SecuritySpy Server"
DEFAULT_BRAND = "Ben Software"
DEFAULT_PORT = 8000
DEFAULT_RECORDING_MODE = "motion"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=2)
DEFAULT_SSL = False

DOMAIN = "securityspy"
NVR_DATA = DOMAIN

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.time_period,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up the Unifi Protect component."""
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST)
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    port = conf.get(CONF_PORT)
    use_ssl = conf.get(CONF_SSL)
    scan_interval = conf[CONF_SCAN_INTERVAL]

    try:
        hass.data[NVR_DATA] = nvr.securityspySvr(
            host, port, username, password, use_ssl
        )
        _LOGGER.debug("Connected to SecuritySpy Platform")

    except requests.exceptions.ConnectionError as ex:
        _LOGGER.error("Unable to connect to NVR: %s", str(ex))
        raise PlatformNotReady

    async def _async_systems_update(now):
        """Refresh internal state for all systems."""
        hass.data[NVR_DATA].update()

        async_dispatcher_send(hass, DOMAIN)

    async_track_time_interval(hass, _async_systems_update, scan_interval)

    return True

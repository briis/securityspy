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
    EVENT_HOMEASSISTANT_START,
    EVENT_HOMEASSISTANT_STOP,
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
ATTR_TRIGGER_TYPE = "last_trigger_type"
ATTR_LAST_TRIGGER = "last_trigger"
ATTR_BRAND = "brand"

CONF_RECORDING_MODE = "recording_mode"

DEFAULT_ATTRIBUTION = "Data provided by SecuritySpy Server"
DEFAULT_BRAND = "Ben Software"
DEFAULT_PORT = 8000
DEFAULT_RECORDING_MODE = "motion"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=2)
DEFAULT_SSL = False

DOMAIN = "securityspy"
NVR_DATA = DOMAIN

SERVICE_SET_RECORDING_MODE = "set_recording_mode"

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


SET_RECORDING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_RECORDING_MODE, default=DEFAULT_RECORDING_MODE): cv.string,
    }
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

    async def async_set_recording_mode(call):
        """Call Set Recording Mode."""
        await async_handle_set_recording_mode(hass, call)

    hass.services.register(
        DOMAIN,
        SERVICE_SET_RECORDING_MODE,
        async_set_recording_mode,
        schema=SET_RECORDING_MODE_SCHEMA,
    )

    async def _async_systems_update(now):
        """Refresh internal state for all systems."""
        hass.data[NVR_DATA].update()

        async_dispatcher_send(hass, DOMAIN)

    async_track_time_interval(hass, _async_systems_update, scan_interval)

    return True

async def async_handle_set_recording_mode(hass, call):
    """Handle enable Always recording."""
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_id = entity_state.attributes[ATTR_CAMERA_ID]
    if camera_id is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return
    
    rec_mode = call.data[CONF_RECORDING_MODE].lower()
    if rec_mode not in {"always", "motion", "never"}:
        rec_mode = "motion"

    def _set_recording_mode(camera_id, recording_mode):
        """Communicate with Camera and set recording mode."""
        hass.data[NVR_DATA].set_camera_recording(camera_id, recording_mode, "motion")

    await hass.async_add_executor_job(
        _set_recording_mode, camera_id, rec_mode
    )

"""
Support for NAD digital amplifiers which can be remote controlled via tcp/ip.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.nadtcp/
"""
import logging
import voluptuous as vol
from homeassistant.components.media_player import (
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_MUTE, SUPPORT_TURN_ON, SUPPORT_TURN_OFF,
    SUPPORT_VOLUME_STEP, SUPPORT_SELECT_SOURCE, MediaPlayerDevice,
    PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_NAME, STATE_OFF, STATE_ON, STATE_UNKNOWN, STATE_UNAVAILABLE, EVENT_HOMEASSISTANT_STOP)
from homeassistant.core import CoreState, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect, dispatcher_send)

import asyncio

REQUIREMENTS = ['nadtcp==0.1.1']

SIGNAL_NAD_STATE_RECEIVED = 'nad_state_received'

_LOGGER = logging.getLogger(__name__)

DEFAULT_RECONNECT_INTERVAL = 10
CONNECTION_TIMEOUT = 10
DEFAULT_NAME = 'NAD amplifier'
DEFAULT_MIN_VOLUME = -60
DEFAULT_MAX_VOLUME = -10
DEFAULT_VOLUME_STEP = 4

SUPPORT_NAD = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | SUPPORT_TURN_ON | \
              SUPPORT_TURN_OFF | SUPPORT_VOLUME_STEP | SUPPORT_SELECT_SOURCE

CONF_MIN_VOLUME = 'min_volume'
CONF_MAX_VOLUME = 'max_volume'
CONF_VOLUME_STEP = 'volume_step'
CONF_RECONNECT_INTERVAL = 'reconnect_interval'
CONF_HOST = 'host'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_RECONNECT_INTERVAL, default=DEFAULT_RECONNECT_INTERVAL): int,
    vol.Optional(CONF_MIN_VOLUME, default=DEFAULT_MIN_VOLUME): int,
    vol.Optional(CONF_MAX_VOLUME, default=DEFAULT_MAX_VOLUME): int,
    vol.Optional(CONF_VOLUME_STEP, default=DEFAULT_VOLUME_STEP): int,
})


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Setup the NAD platform."""
    from nadtcp import NADC338Protocol

    async_add_devices([NADDevice(
        NADC338Protocol,
        config.get(CONF_NAME),
        config.get(CONF_HOST),
        config.get(CONF_RECONNECT_INTERVAL),
        config.get(CONF_MIN_VOLUME),
        config.get(CONF_MAX_VOLUME),
        config.get(CONF_VOLUME_STEP),
    )])

    return True


class NADDevice(MediaPlayerDevice):
    """Device handler for the NAD protocol"""

    def __init__(self, protocol_class, name, host, reconnect_interval, min_volume, max_volume, volume_step):
        """Initialize the device properties"""
        self._protocol_class = protocol_class
        self._protocol = None
        self._name = name
        self._host = host
        self._reconnect_interval = reconnect_interval
        self._min_vol = min_volume
        self._max_vol = max_volume
        self._volume_step = volume_step

        self._state = STATE_UNKNOWN
        self._muted = None
        self._volume = None
        self._source = None

    def nad_vol_to_internal_vol(self, nad_vol):
        """Convert the configured volume range to internal volume range.
        Takes into account configured min and max volume.
        """
        if nad_vol is None:
            volume_internal = 0.0
        elif nad_vol < self._min_vol:
            volume_internal = 0.0
        elif nad_vol > self._max_vol:
            volume_internal = 1.0
        else:
            volume_internal = (nad_vol - self._min_vol) / \
                              (self._max_vol - self._min_vol)
        return volume_internal

    def internal_vol_to_nad_vol(self, internal_vol):
        return int(round(internal_vol * (self._max_vol - self._min_vol) + self._min_vol))

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def source(self):
        """Name of the current input source."""
        return self._source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._protocol_class.AVAILABLE_SOURCES

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_NAD

    async def async_turn_off(self):
        """Turn the media player off."""
        if self._protocol:
            self._protocol.power_off()

    async def async_turn_on(self):
        """Turn the media player on."""
        if self._protocol:
            self._protocol.power_on()

    async def async_volume_up(self):
        """Step volume up in the configured increments."""
        if self._protocol:
            self._protocol.volume_up()

    async def async_volume_down(self):
        """Step volume down in the configured increments."""
        if self._protocol:
            self._protocol.volume_down()

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        if self._protocol:
            self._protocol.set_volume(self.internal_vol_to_nad_vol(volume))

    async def async_mute_volume(self, mute):
        """Mute (true) or unmute (false) media player."""
        if self._protocol:
            if mute:
                self._protocol.mute()
            else:
                self._protocol.unmute()

    async def async_select_source(self, source):
        """Select input source."""
        if self._protocol:
            self._protocol.select_source(source)

    async def async_added_to_hass(self):
        import nadtcp

        def handle_state(state):
            if nadtcp.CMD_VOLUME in state:
                self._volume = self.nad_vol_to_internal_vol(state[nadtcp.CMD_VOLUME])
            if nadtcp.CMD_POWER in state:
                self._state = STATE_ON if state[nadtcp.CMD_POWER] == nadtcp.MSG_ON else STATE_OFF
            if nadtcp.CMD_MUTE in state:
                self._muted = state[nadtcp.CMD_MUTE] == nadtcp.MSG_ON
            if nadtcp.CMD_SOURCE in state:
                self._source = state[nadtcp.CMD_SOURCE]

            self.schedule_update_ha_state()

        def state_changed(state):
            dispatcher_send(self.hass, SIGNAL_NAD_STATE_RECEIVED, state)

        def disconnected(exc=None):
            if self.hass.state != CoreState.stopping:
                _LOGGER.warning('Disconnected from %s, reconnecting', self._host)

                self._state = STATE_UNAVAILABLE
                self.schedule_update_ha_state()
                self.hass.async_add_job(connect)

        async def connect():
            _LOGGER.debug('Connecting to %s', self._host)

            connection = self._protocol_class.create_nad_connection(
                loop=self.hass.loop,
                target_ip=self._host,
                disconnect_cb=disconnected,
                state_changed_cb=state_changed)

            try:
                transport, protocol = await asyncio.wait_for(connection, timeout=CONNECTION_TIMEOUT,
                                                             loop=self.hass.loop)
            except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as exc:
                _LOGGER.exception(
                    "Error connecting to %s, reconnecting in %ss", self._host,
                    self._reconnect_interval)
                self.hass.loop.call_later(self._reconnect_interval, disconnected, exc)
                return

            self._protocol = protocol

            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP,
                                            lambda x: transport.close())

            await self._protocol.state(force_refresh=True)

        async_dispatcher_connect(self.hass, SIGNAL_NAD_STATE_RECEIVED, handle_state)

        self.hass.async_add_job(connect)

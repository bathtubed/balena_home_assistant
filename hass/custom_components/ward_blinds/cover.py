import logging

import voluptuous as vol
import time

# Import the device class from the component that you want to support
from homeassistant.components.cover import CoverDevice, ATTR_TILT_POSITION, DEVICE_CLASS_BLIND, STATE_OPENING, STATE_OPEN, STATE_CLOSING, STATE_CLOSED, SUPPORT_OPEN, SUPPORT_OPEN_TILT, SUPPORT_CLOSE_TILT, SUPPORT_SET_TILT_POSITION, PLATFORM_SCHEMA

from homeassistant.helpers.entity import Entity

from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv


REST, CLOSING, OPENING = tuple(range(3))

DOMAIN="ward_blinds"
_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default='Blinds'): cv.string,
})

ATTR_NAME = 'name'
DEFAULT_OPEN_NAME = "Morning"
DEFAULT_CLOSE_NAME = "Evening"

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Awesome Light platform."""
    
    name = config.get(CONF_NAME)
    blinds = hass.data[DOMAIN+'.'+name]
    
    def scheduled_open(call):
        name = call.data.get(ATTR_NAME, DEFAULT_OPEN_NAME)
        blinds.schedule_recurring(name, time.time(), 24*60*60, "open_blinds")
    
    def scheduled_close(call):
        name = call.data.get(ATTR_NAME, DEFAULT_CLOSE_NAME)
        blinds.schedule_recurring(name, time.time(), 24*60*60, "close_blinds")

    # Verify that passed in configuration works
    try:
        discard = blinds.get_position()
    except Exception as err:
        _LOGGER.error("Failed to connect to blinds %s: ", name, err)
    else:
        # Add devices
        add_devices([WardBlinds(blinds, name)])
        hass.services.register(DOMAIN, 'scheduled_open', scheduled_open)
        hass.services.register(DOMAIN, 'scheduled_close', scheduled_close)

class WardBlinds(CoverDevice):
    """Representation of an Awesome Light."""

    def __init__(self, blinds, name):
        self._blinds = blinds
        self._closed = None
        self._name = name
        self._amount_open = None
        self._max_open = None
        self._state = None
        self._most_recent_rest = time.time()

    @property
    def name(self):
        # Return the display name of this light.
        return self._name
    
    @property
    def device_class(self):
        return DEVICE_CLASS_BLIND
    
    @property
    def supported_features(self):
        return SUPPORT_OPEN_TILT | SUPPORT_CLOSE_TILT | SUPPORT_SET_TILT_POSITION

    @property
    def current_cover_tilt_position(self):
        # Return the amount out of 100 the blinds are open.
        return int((self._amount_open / self._max_open) * 100)

    @property
    def is_closed(self):
        # Return true if blinds are at all open.
        return self._closed
    
    @property
    def is_opening(self):
        return self._state == OPENING
    
    @property
    def is_closing(self):
        return self._state == CLOSING

    def open_cover_tilt(self, **kwargs):
        # Open the blinds
        
        amount = int((kwargs.get(ATTR_TILT_POSITION, 100) / 100) * self._max_open)
        self._blinds.set_blinds(amount)
        self._state = OPENING
        self._most_recent_rest = time.time()

    def close_cover_tilt(self, **kwargs):
        # Close the blinds
        self._state = CLOSING
        self._blinds.close_blinds()
    
    def set_cover_tilt_position(self, **kwargs):
        self.open_cover_tilt(**kwargs)

    def update(self):
        # Update the blinds state
        
        batch = self._blinds.batch()
        batch.get_state()
        batch.closed()
        batch.get_config()
        batch.get_position()
        
        STATE, CLOSED, CONFIG, POSITION = tuple(range(4))
        
        results = tuple(batch())
        
        self._state = results[STATE]
        self._max_open = results[CONFIG]['hardware_config']['open_millis']

        # Checks if its moving, if so, extrapolates the amount opened so far
        if self._state == REST:
            self._most_recent_rest = time.time()
            self._closed = results[CLOSED]
            self._amount_open = results[POSITION]
        elif self._state == OPENING:
            self._amount_open = results[POSITION] + (time.time() - self._most_recent_rest)*1000
            self._closed = False
        elif self._state == CLOSING:
            self._amount_open = results[POSITION] - (time.time() - self._most_recent_rest)*1000
            self._closed = results[CLOSED]

import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light, PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
import homeassistant.helpers.config_validation as cv

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['jsonrpclib-pelix==0.3.2']

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default='Blinds'): cv.string,
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})

ATTR_NAME = 'name'
DEFAULT_OPEN_NAME = "Morning"
DEFAULT_CLOSE_NAME = "Evening"

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Awesome Light platform."""
    import jsonrpclib as jrpc, base64, time

    # Assign configuration variables. The configuration check takes care they are
    # present.
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    headers = {}
    if username:
        auth_tok = base64.encodestring(username+':'+password).replace('\n', '')
        headers = {'Authorization' : 'Basic ' + auth_tok}
    
    # Setup connection with devices/cloud
    blinds = jrpc.ServerProxy(host, headers=headers)
    
    def scheduled_open(call):
        name = call.data.get('name', DEFAULT_OPEN_NAME)
        blinds.schedule_recurring(name, time.time(), 24*60*60, "open_blinds")
    
    def scheduled_close(call):
        name = call.data.get('name', DEFAULT_CLOSE_NAME)
        blinds.schedule_recurring(name, time.time(), 24*60*60, "close_blinds")

    # Verify that passed in configuration works
    try:
        discard = blinds.get_position()
    except:
        _LOGGER.error("Failed to connect to blinds on %s as user %s", host, username)
    else:
        # Add devices
        add_devices([WardBlinds(blinds, name)])
        hass.services.register('light', 'ward_blinds_scheduled_on', scheduled_open)
        hass.services.register('light', 'ward_blinds_scheduled_off', scheduled_close)



class WardBlinds(Light):
    """Representation of an Awesome Light."""

    def __init__(self, blinds, name):
        self._blinds = blinds
        self._state = None
        self._name = name
        self._amount_open = None
        self._max_open = None

    @property
    def name(self):
        # Return the display name of this light.
        return self._name

    @property
    def brightness(self):
        # Return the amount out of 255 the blinds are open.
        return (self._amount_open / self._max_open) * 255

    @property
    def is_on(self):
        # Return true if blinds are at all open.
        return self._state
    
    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    def turn_on(self, **kwargs):
        # Open the blinds
        
        # feed forward the local state
        self._state = True
        self._amount_open = int((kwargs.get(ATTR_BRIGHTNESS, 255) / 255) * self._max_open)
        self._blinds.set_blinds(self._amount_open)
        
        # Wait for the blinds to start moving
        while self._blinds.get_state() == 0 and self._blinds.get_position() != self._amount_open:
            pass

    def turn_off(self, **kwargs):
        # Close the blinds
        self._amount_open = 0
        self._state = False
        self._blinds.close_blinds()
        
        # Wait for the blinds to start moving
        while self._blinds.get_state() == 0 and not self._blinds.closed():
            pass

    def update(self):
        # Update the blinds state
        # Checks if its moving, if so, doesn't update, keeps most recent values
        if self._blinds.get_state() == 0:
            _LOGGER.info("Updating state")
            self._state = not self._blinds.closed()
            self._max_open = self._blinds.get_config()['hardware_config']['open_millis']
            self._amount_open = self._blinds.get_position()

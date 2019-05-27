import logging

import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA

from homeassistant.const import CONF_NAME, DEVICE_CLASS_ILLUMINANCE
import homeassistant.helpers.config_validation as cv

DOMAIN="ward_blinds"
_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default='Blinds'): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    blinds = hass.data[DOMAIN+'.'+name]
    
    # Verify that passed in configuration works
    try:
        discard = blinds.get_lux()
    except Exception as err:
        _LOGGER.error("Failed to connect to sensor %s: ", name, err)
    else:
        # Add devices
        add_devices([BlindsSensor(blinds, name)])

class BlindsSensor(Entity):
    """ Representation of the sensor attached to the WardBlinds """
    
    def __init__(self, blinds, name):
        self._blinds = blinds
        self._state = None
        self._name = name
    
    @property
    def name(self):
        return self._name
    
    @property
    def state(self):
        return self._state
    
    @property
    def unit_of_measurement(self):
        return "lx"
    
    @property
    def device_class(self):
        return DEVICE_CLASS_ILLUMINANCE
    
    def update(self):
        self._state = self._blinds.get_lux()

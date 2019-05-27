import logging
import threading
from types import MethodType

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
import homeassistant.helpers.config_validation as cv

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['jsonrpclib-pelix>=0.4.0']

DOMAIN="ward_blinds"
_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default='Blinds'): cv.string,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    })
}, extra = vol.ALLOW_EXTRA)

def setup(hass, config):
    import jsonrpclib as jrpc, base64, time

    # Assign configuration variables. The configuration check takes care they are
    # present.
    config = config[DOMAIN]
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
    blinds.batch = lambda: jrpc.MultiCall(blinds)
    
    lock = threading.RLock()
    def sync_request(self, request, notify=False):
        with lock:
            return jrpc.ServerProxy._run_request(self, request, notify)
    
    blinds._run_request = MethodType(sync_request, blinds)
    
    hass.data[DOMAIN+'.'+name] = blinds
    
    return True

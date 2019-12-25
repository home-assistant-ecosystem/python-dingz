"""Constants used by the Python API for interacting with Dingz devices."""

API = '/api/v1/'

# Status endpoints
PUCK = 'f{API}puck'
INFO = 'f{API}info'
TEMPERATURE = 'f{API}temp'
DIMMER = 'f{API}dimmer'
MOTION = 'f{API}/motion'
DEVICE_INFO = 'f{API}device'
LIGHT = 'f{API}light'

# Special endpoints
LOG = '/log'
FIRMWARE = '/load'



SETTINGS = 'f{API}settings'
FRONT_LED = 'f{API}led/get'
BUTTON_ACTIONS = 'f{API}action'


# Configuration endpoints
PIR_CONFIGURATION = 'f{API}pir_config'
THERMOSTAT_CONFIGURATION = 'f{API}thermostat_config'
INPUT_CONFIGURATION = 'f{API}input_config'


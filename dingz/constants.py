"""Constants used by the Python API for interacting with dingz units."""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("setuptools").version
except Exception:
    __version__ = "unknown"

TIMEOUT = 10

USER_AGENT = f"PythonDingz/{__version__}"
API = "/api/v1/"

# Status endpoints
PUCK = "puck"
INFO = "info"
TEMPERATURE = "temp"
DIMMER = "dimmer"
MOTION = "motion"
DEVICE_INFO = "device"
LIGHT = "light"
SCHEDULE = "schedule"
TIMER = "timer"
SHADE = "shade"
STATE = "state"

# Special endpoints
LOG = "/log"
FIRMWARE = "/load"

SETTINGS = "settings"
SYSTEM_CONFIG = "system_config"
FRONT_LED_GET = "led/get"
FRONT_LED_SET = "led/set"
BUTTON_ACTIONS = "action"
WIFI_SCAN = "scan"

# Configuration endpoints
PIR_CONFIGURATION = "pir_config"
BLIND_CONFIGURATION = "blind_config"
DIMMER_CONFIGURATION = "dimmer_config"
THERMOSTAT_CONFIGURATION = "thermostat_config"
INPUT_CONFIGURATION = "input_config"

# Communication constants
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE = "Content-Type"
CONTENT_TYPE_TEXT_PLAIN = "text/plain"

DEVICE_MAPPING = {
    "102": "myStrom Bulb",
    "108": "dingz",
}

"""Python client/wrapper to interact with dingz devices."""
import logging

import aiohttp
from yarl import URL

from . import make_call
from .constants import (
    API,
    BUTTON_ACTIONS,
    DEVICE_INFO,
    FRONT_LED_GET,
    FRONT_LED_SET,
    INPUT_CONFIGURATION,
    LIGHT,
    PIR_CONFIGURATION,
    PUCK,
    SETTINGS,
    TEMPERATURE,
    THERMOSTAT_CONFIGURATION,
    WIFI_SCAN,
    TIMER,
    SCHEDULE,
    INFO,
    STATE,
    SYSTEM_CONFIG,
    BLIND_CONFIGURATION,
    DIMMER_CONFIGURATION, SHADE,
)
from .dimmer import DimmerRegistry
from .shade import ShadeRegistry

_LOGGER = logging.getLogger(__name__)


class Dingz:
    """A class for handling the communication with a dingz device."""

    def __init__(self, host: str, session: aiohttp.client.ClientSession = None) -> None:
        """Initialize the dingz."""
        self._close_session = False
        self._host = host
        self._session = session
        self._device_details = None
        self._info = None
        self._wifi_networks = None
        self._settings = None
        self._catch_all = {}
        self._button_action = None
        self._temperature = None
        self._intensity = None
        self._day = None
        self._night = None
        self._hour_of_day = None
        self._motion = None
        self._schedule = None
        self._timer = None
        self._state = {}
        self._blind_config = None
        self._dimmer_config = None
        self._system_config = None
        self._devices_config = None

        self._dimmers = DimmerRegistry(dingz=self)
        self._shades = ShadeRegistry(dingz=self)

        self.uri = URL.build(scheme="http", host=self._host).join(URL(API))

    async def get_device_info(self) -> None:
        """Get the details from the dingz."""
        url = URL(self.uri).join(URL(DEVICE_INFO))
        response = await make_call(self, uri=url)
        # response is:  "mac" => { device_details }
        self._device_details = next(iter(response.values()))

    async def get_info(self) -> None:
        """Get general information fro the dingz."""
        url = URL(self.uri).join(URL(INFO))
        response = await make_call(self, uri=url)
        self._info = response

    async def get_all_info(self) -> None:
        """Get everything from the dingz unit."""
        for endpoint in [
            PUCK,
            DEVICE_INFO,
            SETTINGS,
            PIR_CONFIGURATION,
            THERMOSTAT_CONFIGURATION,
            INPUT_CONFIGURATION,
            BUTTON_ACTIONS,
        ]:
            url = URL(self.uri).join(URL(endpoint))
            self._catch_all[endpoint] = await make_call(self, uri=url)

    async def get_settings(self) -> None:
        """Get the settings from the dingz."""
        url = URL(self.uri).join(URL(SETTINGS))
        self._settings = await make_call(self, uri=url)

    async def get_wifi_networks(self) -> None:
        """Get the Wifi networks in range."""
        url = URL(self.uri).join(URL(WIFI_SCAN))
        self._wifi_networks = await make_call(self, uri=url)

    async def get_schedule(self) -> None:
        """Get the available schedules."""
        url = URL(self.uri).join(URL(SCHEDULE))
        self._schedule = await make_call(self, uri=url)

    async def get_timer(self) -> None:
        """Get the available timers."""
        url = URL(self.uri).join(URL(TIMER))
        self._timer = await make_call(self, uri=url)

    async def get_configuration(self, part) -> None:
        """Get the configuration of a dingz part."""
        urls = {
            "pir": PIR_CONFIGURATION,
            "thermostat": THERMOSTAT_CONFIGURATION,
            "input": INPUT_CONFIGURATION,
        }
        url_part = [value for key, value in urls.items() if part in key][0]
        url = URL(self.uri).join(URL(url_part))
        self._configuration = await make_call(self, uri=url)

    async def get_temperature(self) -> None:
        """Get the room temperature from the dingz."""
        url = URL(self.uri).join(URL(TEMPERATURE))
        response = await make_call(self, uri=url)
        self._temperature = response["temperature"]

    async def get_button_action(self) -> None:
        """Get the room temperature from the dingz."""
        url = URL(self.uri).join(URL(BUTTON_ACTIONS))
        self._button_action = await make_call(self, uri=url)

    async def get_light(self) -> None:
        """Get the light details from the switch."""
        url = URL(self.uri).join(URL(LIGHT))
        response = await make_call(self, uri=url)
        self._intensity = response["intensity"]
        self._hour_of_day = response["state"]

    def _consume_sensor_state(self, response):
        self._intensity = response["brightness"]
        self._hour_of_day = response["light_state"]
        self._temperature = response["room_temperature"]
        self._motion = response["person_present"] == 1

    async def get_state(self) -> None:
        """Fetch the current state and update the different internal representations."""

        # first fetch the device state
        url = URL(self.uri).join(URL(STATE))
        device_state = await make_call(self, uri=url)
        self._consume_sensor_state(device_state['sensors'])
        self._dimmers._consume_dimmer_state(device_state['dimmers'])
        self._shades._consume_device_state(device_state['blinds'])
        self._state = device_state

        if len(self._shades.all()) > 0:
            # for shades, we want to call shade api as well, as it contains the current positions
            url = URL(self.uri).join(URL(SHADE))
            shade_state = await make_call(self, uri=url)
            self._shades._consume_shade_state(shade_state.values())

    async def get_blind_config(self) -> None:
        """Get the configuration of the blinds."""
        url = URL(self.uri).join(URL(BLIND_CONFIGURATION))
        response = await make_call(self, uri=url)
        self._blind_config = response['blinds']

    async def get_dimmer_config(self) -> None:
        """Get the configuration of the dimmer/lights."""
        url = URL(self.uri).join(URL(DIMMER_CONFIGURATION))
        response = await make_call(self, uri=url)
        self._dimmer_config = response['dimmers']

    async def get_system_config(self) -> None:
        """Get the system configuration of a dingz."""
        url = URL(self.uri).join(URL(SYSTEM_CONFIG))
        response = await make_call(self, uri=url)
        self._system_config = response

    async def get_devices_config(self) -> None:
        """
        Try to determine the full devices configuration of the device.

        Load the blind/dimmer config. Determine what is attached, and resolve the names.
        """
        await self.get_state()
        await self.get_blind_config()
        await self.get_dimmer_config()

        # all blinds/dimmers are visible in the device config, regardless of their dip state.
        # => later in the getter, we correlate the config against the current state and
        #    can determine if a object is actually in use

        self._shades._consume_config(self._blind_config)
        self._dimmers._consume_config(self._dimmer_config)

    async def enabled(self) -> bool:
        """Return true if front LED is on."""
        url = URL(self.uri).join(URL(FRONT_LED_GET))
        response = await make_call(self, uri=url)
        return bool(response["on"])

    async def turn_on(self) -> None:
        """Enable/turn on the front LED."""
        data = {"action": "on"}
        url = URL(self.uri).join(URL(FRONT_LED_SET))
        await make_call(self, uri=url, method="POST", data=data)

    async def turn_off(self) -> None:
        """Disable/turn off the front LED."""
        data = {"action": "off"}
        url = URL(self.uri).join(URL(FRONT_LED_SET))
        await make_call(self, uri=url, method="POST", data=data)

    async def set_timer(self, data) -> None:
        """Set a timer."""
        print(data)
        url = URL(self.uri).join(URL(TIMER))
        await make_call(self, uri=url, method="POST", json_data=data)

    async def stop_timer(self, data) -> None:
        """Stop a timer."""
        url = URL(self.uri).join(URL(TIMER))
        await make_call(self, uri=url, method="POST", data=data)

    @property
    def shades(self) -> ShadeRegistry:
        """
        test
        :return: a ShadeRegistry
        """
        return self._shades

    @property
    def dimmers(self) -> DimmerRegistry:
        return self._dimmers

    @property
    def dingz_name(self) -> str:
        """Get the name of a dingz."""
        return self._system_config["dingz_name"]

    @property
    def device_details(self) -> str:
        """Return the current device details."""
        return self._device_details

    @property
    def settings(self) -> str:
        """Return the current device settings."""
        return self._settings

    @property
    def schedule(self) -> str:
        """Return the schedule details."""
        return self._schedule

    @property
    def timer(self) -> str:
        """Return the timer details."""
        return self._timer

    @property
    def configuration(self) -> str:
        """Return the current configuration of a dingz part."""
        return self._configuration

    @property
    def wifi_networks(self) -> str:
        """Return the WiFi networks in range."""
        return self._wifi_networks

    @property
    def everything(self) -> dict:
        """Return the all available device details."""
        return self._catch_all

    @property
    def button_action(self) -> float:
        """Return the current button action."""
        return self._button_action

    @property
    def temperature(self) -> float:
        """Return the current temperature in celsius."""
        return round(self._temperature, 1)

    @property
    def motion(self) -> bool:
        """Return true if the sensor is detecting motion."""
        return self._motion

    @property
    def day(self) -> bool:
        """Return true if the sensor thinks it's day."""
        return True if self._hour_of_day == "day" else False

    @property
    def night(self) -> bool:
        """Return true if the sensor thinks it's night."""
        return True if self._hour_of_day == "night" else False

    @property
    def intensity(self) -> float:
        """Return the current light intensity in lux."""
        return round(self._intensity, 1)

    @property
    def version(self) -> str:
        """Return the version of a dingz."""
        return self._info["version"]

    @property
    def type(self) -> str:
        """Return the type of a dingz."""
        return self._info["type"]

    @property
    def mac(self) -> str:
        """Return the MAC address of a dingz."""
        return self._info["mac"]

    @property
    def front_hw_model(self) -> str:
        """Get the hardware model of a dingz."""
        return self._device_details["front_hw_model"]

    @property
    def puck_hw_model(self) -> str:
        """Get the hardware model of a dingz puck."""
        return self._device_details["puck_hw_model"]

    @property
    def front_serial_number(self) -> str:
        """Get the serial_number of the a dingz front."""
        return self._device_details["front_sn"]

    @property
    def puck_serial_number(self) -> str:
        """Get the serial number of a dingz puck."""
        return self._device_details["puck_sn"]

    @property
    def hw_version(self) -> str:
        """Get the hardware version of a dingz."""
        return self._device_details["hw_version"]

    @property
    def fw_version(self) -> str:
        """Get the firmware version of a dingz."""
        return self._device_details["fw_version"]

    # See "Using Asyncio in Python" by Caleb Hattingh for implementation
    # details.
    async def close(self) -> None:
        """Close an open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "Dingz":
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()

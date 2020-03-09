"""A Python Client to interact with Dingz devices."""
import logging
import json
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
)

_LOGGER = logging.getLogger(__name__)


class Dingz:
    """A class for handling the communication with a dingz device."""

    def __init__(self, host: str, session: aiohttp.client.ClientSession = None) -> None:
        """Initialize the dingz."""
        self._close_session = False
        self._host = host
        self._session = session
        self._device_details = None
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
        self.uri = URL.build(scheme="http", host=self._host).join(URL(API))

    async def get_device_info(self) -> None:
        """Get the details from the dingz."""
        url = URL(self.uri).join(URL(DEVICE_INFO))
        response = await make_call(self, uri=url)
        self._device_details = response

    async def get_info(self) -> None:
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
    def everything(self) -> str:
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
        return None

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

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
    SHADE,
    INFO,
    STATE,
    SYSTEM_CONFIG,
    BLIND_CONFIGURATION,
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
        self._system_config = None

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

    async def get_state(self) -> None:
        """Get the state."""
        url = URL(self.uri).join(URL(STATE))
        response = await make_call(self, uri=url)
        self._state = response

    async def get_blind_config(self) -> None:
        """Get the configuration of a dingz blind part."""
        url = URL(self.uri).join(URL(BLIND_CONFIGURATION))
        response = await make_call(self, uri=url)
        self._blind_config = response

    async def get_system_config(self) -> None:
        """Get the system configuration of a dingz."""
        url = URL(self.uri).join(URL(SYSTEM_CONFIG))
        response = await make_call(self, uri=url)
        self._system_config = response

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

    async def operate_shade(self, shade_no, blind=None, lamella=None) -> None:
        """Operate the lamella and blind.

        blind: 0 fully closed, 100 fully open
        lamella: 0 lamellas closed, 100 lamellas open
        """

        # With newer versions of dingz, we can just leave
        # either lamella or blind None (i.e. do not chang)
        # but currently we need to lookup the current state
        # of the shade first.
        if blind is None or lamella is None:
            await self.get_state()

            if blind is None:
                blind = self.current_blind_level(shade_no)

            if lamella is None:
                if self.is_shade_opened(shade_no):
                    # If the shade is currently completely opened (i.e. up), the lamella
                    # value is not really relevant (has no effect). We assume the
                    # lamella value to be 0, ie. closed.
                    # i.e. we set lamella to 45, raise blind to the top, and then back down again
                    # => de we expect the lamella to be set to 45 again, or does it get resetted to 0?
                    lamella = 0
                else:
                    lamella = self.current_lamella_level(shade_no)

        url = URL(self.uri).join(URL("%s/%s" % (SHADE, shade_no)))
        params = {"blind": str(blind), "lamella": str(lamella)}
        await make_call(self, uri=url, method="POST", parameters=params)

    async def shade_up(self, shade_no) -> None:
        """Move the shade up."""
        await self.shade_command(shade_no, "up")

    async def shade_down(self, shade_no) -> None:
        """Move the shade down."""
        await self.shade_command(shade_no, "down")

    async def shade_stop(self, shade_no) -> None:
        """Stop the shade."""
        await self.shade_command(shade_no, "stop")

    async def lamella_open(self, shade_no) -> None:
        """Open the lamella."""
        await self.operate_shade(shade_no, lamella=100)

    async def lamella_close(self, shade_no) -> None:
        """Close the lamella."""
        await self.operate_shade(shade_no, lamella=0)

    async def lamella_stop(self, shade_no) -> None:
        """Stop the lamella."""
        await self.shade_stop(shade_no)

    async def shade_command(self, shade_no, verb):
        """Create a command for the shade."""
        url = URL(self.uri).join(URL("%s/%s/%s" % (SHADE, shade_no, verb)))
        await make_call(self, uri=url, method="POST")

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

    def _shade_current_state(self, shade_no: int):
        """Get the configuration of the shade."""
        return self._state["blinds"][shade_no]

    def current_blind_level(self, shade_no):
        """Get the current blind level."""
        return self._shade_current_state(shade_no)["position"]

    def current_lamella_level(self, shade_no):
        """Get the current lamella level."""
        return self._shade_current_state(shade_no)["lamella"]

    def is_shade_closed(self, shade_no):
        """Get the closed state of a shade."""
        # When closed, we care if the lamellas are opened or not
        return (
            self.current_blind_level(shade_no) == 0
            and self.current_lamella_level(shade_no) == 0
        )

    def is_shade_opened(self, shade_no):
        """Get the open state of a shade."""
        return self.current_blind_level(shade_no) == 100

    def is_lamella_closed(self, shade_no):
        """Get the closed state of a lamella."""
        return self.current_lamella_level(shade_no) == 0

    def is_lamella_opened(self, shade_no):
        """Get the open state of  lamella."""
        return self.current_lamella_level(shade_no) == 100

    def is_blind_opening(self, shade_no):
        """Get the state of the blind if opening."""
        return self._shade_current_state(shade_no)["moving"] == "up"

    def is_blind_closing(self, shade_no):
        """Get the state of the blind if closing."""
        return self._shade_current_state(shade_no)["moving"] == "down"

    def blind_name(self, shade_no):
        """Get the name of the blind."""
        return self._blind_config["blinds"][shade_no]["name"]

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

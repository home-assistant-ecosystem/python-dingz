"""A Python Client to interact with Dingz devices."""
import logging

import aiohttp
from yarl import URL

from . import _request as request
from .constants import API, DEVICE_INFO, TEMPERATURE, LIGHT

_LOGGER = logging.getLogger(__name__)


class Dingz:
    """A class for handling the communication with a dingz device."""

    def __init__(self, host: str, session: aiohttp.client.ClientSession = None) -> None:
        """Initialize the dingz."""
        self._close_session = False
        self._host = host
        self._session = session
        self._device_details = None
        self._temperature = None
        self._intensity = None
        self._day = None
        self.uri = URL.build(scheme="http", host=self._host).join(URL(API))

    async def get_device_info(self) -> None:
        """Get the details from the dingz."""
        url = URL(self.uri).join(URL(DEVICE_INFO))
        response = await request(self, uri=url)
        self._device_details = response

    async def get_temperature(self) -> None:
        """Get the room temperature from the dingz."""
        url = URL(self.uri).join(URL(TEMPERATURE))
        response = await request(self, uri=url)
        self._temperature = response["temperature"]

    async def get_light(self) -> None:
        """Get the light details from the switch."""
        url = URL(self.uri).join(URL(LIGHT))
        response = await request(self, uri=url)
        self._intensity = response["intensity"]
        self._day = response["day"]

    @property
    def device_details(self) -> str:
        """Return the current device details."""
        return self._device_details

    @property
    def temperature(self) -> float:
        """Return the current temperature in celsius."""
        return round(self._temperature, 1)

    @property
    def day(self) -> bool:
        """Return true if the sensor thinks it's day."""
        return bool(self._day)

    @property
    def intensity(self) -> float:
        """Return the current light intensity in lux."""
        return round(self._intensity, 1)

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

"""A Python Client to interact with Dingz devices."""
import logging

import aiohttp
from yarl import URL

from . import _request as request
from .constants import API, DEVICE_INFO, TEMPERATURE

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
        self.uri = URL.build(scheme="http", host=self._host).join(URL(API))

    async def get_device_info(self) -> None:
        """Get the details from the switch."""
        url = URL(self.uri).join(URL(DEVICE_INFO))
        response = await request(self, uri=url)
        self._device_details = response

    async def get_temperature(self) -> None:
        """Get the details from the switch."""
        url = URL(self.uri).join(URL(TEMPERATURE))
        response = await request(self, uri=url)
        self._temperature = response["temperature"]

    @property
    def device_details(self) -> float:
        """Return the current device details."""
        return self._device_details

    @property
    def temperature(self) -> float:
        """Return the current temperature in celsius."""
        return round(self._temperature, 1)

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

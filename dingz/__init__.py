"""A Python Client to interact with Dingz devices."""
import asyncio
import logging

import aiohttp
import async_timeout

from . import exceptions
from .constants import TEMPERATURE, MOTION, LIGHT, PUCK, INFO

_LOGGER = logging.getLogger(__name__)


class Dingz:
    """A class for handling the communication with a Dingz device."""

    def __init__(self, device, loop, session):
        """Initialize the connection."""
        self._loop = loop
        self._session = session
        self.token = None
        self.device = device
        self.data = None

    async def get_data(self, endpoint):
        """Retrieve the data from a given endpoint."""
        try:
            with async_timeout.timeout(5, loop=self._loop):
                response = await self._session.get(f"{endpoint}")

            _LOGGER.debug("Response from Dingz device: %s", response.status)
            self.data = await response.json()
            _LOGGER.debug(self.data)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Can not load data from Dingz device")
            self.data = None
            raise exceptions.DingzConnectionError()

    @property
    def info(self):
        """Get the state of the motion sensor."""
        data = await self.get_data(INFO)
        return data['motion']

    @property
    def puck(self):
        """Get the state of the hardware."""
        data = await self.get_data(PUCK)
        if self.data is not None:
            return {'firmware': data['fw']['version'], 'hardware': data['hw']['version']}

    @property
    def temperature(self):
        """Get the temperature."""
        data = await self.get_data(TEMPERATURE)
        return round(data['temperature'], 2)

    @property
    def light(self):
        """Get the brightness."""
        data = await self.get_data(LIGHT)
        return round(data['intensity'], 2)

    @property
    def day(self):
        """Get the state if daytime or not."""
        data = await self.get_data(LIGHT)
        return data['day']

    @property
    def motion(self):
        """Get the state of the motion sensor."""
        data = await self.get_data(MOTION)
        return data['motion']




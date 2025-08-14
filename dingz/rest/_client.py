from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import aiohttp
from typing_extensions import Self
from yarl import URL

from dingz.constants import CONTENT_TYPE_JSON, CONTENT_TYPE_TEXT_PLAIN, USER_AGENT

if TYPE_CHECKING:
    from types import TracebackType

    from ._types import Device, NetworkInfo, Ram, State


class RestClient:
    """Low-level REST client for the dingz API.

    This class can be used as a context manager.
    """

    def __init__(
        self,
        /,
        host: str | URL,
        *,
        session: aiohttp.ClientSession | None = None,
        session_owner: bool = False,
    ) -> None:
        """Initialize the REST client.

        Args:
            host: The hostname or base URL for the API.
            session: An existing aiohttp ClientSession to use. If None, a new session will be
                     created. Defaults to None.
            session_owner: Indicates whether this client owns the session and is responsible for
                           closing it. Ignored if no session is provided. Defaults to False.

        """
        if session is None:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    ssl=False,
                )
            )
            self._session_owner = True
        else:
            self._session = session
            self._session_owner = session_owner

        self._base_url = host if isinstance(host, URL) else URL.build(scheme="http", host=host)
        self._headers = {
            "User-Agent": USER_AGENT,
            "Accept": f"{CONTENT_TYPE_JSON}, {CONTENT_TYPE_TEXT_PLAIN}, */*",
        }
        self._timeout = aiohttp.ClientTimeout(total=10.0)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(host={self._base_url!r})"

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the REST client.

        If the underlying session is owned by this client, it will be closed.
        """
        if self._session_owner:
            await self._session.close()

    async def _request(self, method: Literal["GET"], endpoint: URL) -> Any:  # noqa: ANN401 The return value really could be anything!
        async with self._session.request(
            method,
            self._base_url.join(endpoint),
            headers=self._headers,
            timeout=self._timeout,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_firmware_version(self) -> str:
        """Get the firmware version of the dingz device.

        This function is designed to be robust against version changes.
        It attempts to get the firmware version from several sources.
        """

        async def from_network_info() -> str:
            nw_info = await self.get_network_info()
            return nw_info["version"]

        async def from_device() -> str:
            device = await self.get_device()
            return device["fw_version"]

        exc: Exception | None = None
        for fn in [from_network_info, from_device]:
            try:
                return await fn()
            # We want to be robust against any kind of error in this function
            except Exception as err:  # noqa: BLE001, PERF203
                if exc is not None:
                    exc.__cause__ = err
                exc = err

        assert exc is not None, "We always make at least one attempt"
        raise exc

    async def get_device(self) -> Device:
        """Get device information.

        This includes device configuration, hardware / software version, manufacturing dates and
        other details.
        """
        # The endpoint actually returns a map of <some id> -> Device.
        # The id isn't the mac or either of the serial numbers.
        devices: dict[str, Device] = await self._request("GET", URL("/api/v1/device"))
        assert len(devices) == 1, "Expected exactly one device in the response"
        device_id, device = next(iter(devices.items()))
        device["device_id"] = device_id  # Add the device id to the device data
        return device

    async def get_network_info(self) -> NetworkInfo:
        """Get general network settings."""
        return await self._request("GET", URL("/api/v1/info"))

    async def get_state(self) -> State:
        """Get the full dingz status.

        Includes the following modules: dimmer, led, sensors, dynamic light, thermostat, wifi and
        cloud.
        """
        return await self._request("GET", URL("/api/v1/state"))

    async def get_ram(self) -> Ram:
        """Get RAM information."""
        return await self._request("GET", URL("/api/v1/ram"))

"""Dingz discovery.

The discovery is based on mDNS.
dingz devices announce a HTTP local TXT service on port 80 over mDNS. Hostname is always in
the form of `DINGZ-<model>-<MAC>`.
Eg.: `DINGZ-dz1f-4b-30C6F72355C4.local TXT`
"""

from __future__ import annotations

import asyncio
import dataclasses
import logging
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import TYPE_CHECKING

from typing_extensions import Self
from zeroconf import ServiceInfo, ServiceListener, Zeroconf
from zeroconf.asyncio import (
    AsyncServiceBrowser,
    AsyncServiceInfo,
    AsyncZeroconf,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Mapping
    from types import TracebackType

__all__ = [
    "Discovery",
    "Properties",
    "discover",
    "discover_list",
]

_LOGGER = logging.getLogger(__name__)

_DINGZ_NAME_PREFIX = "DINGZ "
_DEFAULT_HTTP_PORT = 80


@dataclasses.dataclass(frozen=True)
class Properties:
    """Properties of a discovered dingz device."""

    fw_version: str
    """The firmware version of the device."""
    protected: bool
    """Whether the device is protected."""
    pir: bool
    """Whether the device has a PIR."""
    id: str
    """Dingz ID.

    This is different from the serial number and can be set by the user.
    """
    home_name: str
    """User provided home name."""
    room_name: str
    """User provided room name."""
    device_name: str
    """User provided device name."""
    mac: str
    """Mac address of the device."""

    @classmethod
    def from_zeroconf_properties(cls, props: Mapping[str, str | None]) -> Self:
        """Read the properties from a zeroconf discovery."""
        return cls(
            fw_version=str(props["fw"]),
            protected=props["protected"] == "true",
            pir=props["pir"] == "true",
            id=str(props["id"]),
            home_name=str(props["home"]),
            room_name=str(props["room"]),
            device_name=str(props["name"]),
            mac=str(props["mac"]),
        )


@dataclasses.dataclass(frozen=True)
class Discovery:
    """A discovered dingz device."""

    host: str
    """Host address of the device."""
    props: Properties
    """Properties of the discovered device."""

    @classmethod
    def from_service_info(cls, info: ServiceInfo) -> Self:
        """Create a Discovery instance from a ServiceInfo instance."""
        props = Properties.from_zeroconf_properties(info.decoded_properties)
        addresses = info.parsed_addresses()
        if not addresses:
            msg = "ServiceInfo has no parsed addresses"
            raise ValueError(msg)
        host = addresses[0]
        if info.port != _DEFAULT_HTTP_PORT:
            host = f"{host}:{info.port}"

        return cls(host=host, props=props)


async def discover_list(duration: float = 10.0) -> list[Discovery]:
    """Discover dingz devices on the network.

    This is a simpler version of the more flexible `discover` function.

    Args:
        duration: The duration to listen for devices (in seconds).

    Returns:
        A list of discovered dingz devices.
    """
    discoveries: list[Discovery] = []

    def callback(discovery: Discovery) -> None:
        discoveries.append(discovery)

    async with _discover_with_callback(callback, timeout=duration) as _:
        await asyncio.sleep(duration)
    return discoveries


def discover(
    *,
    duration: float | None = None,
    timeout: float = 10.0,
) -> AbstractAsyncContextManager[AsyncIterator[Discovery]]:
    """Discover dingz devices on the network.

    This function is an async context manager. Entering it starts the discovery process and returns
    an async iterator which yields the discoveries as they are made.

    Consider using the `discover_list` function with a simpler interface if you don't need to get
    discoveries in real-time.

    Args:
        duration: The time in seconds to perform discovery. `None` means forever (or until the
                  context manager is exited). Any pending discoveries will still be yielded.
        timeout: Timeout for requesting service info from a discovered device. This is an advanced
                 parameter and likely doesn't need to be changed.

    Example:
        async with discover() as discoveries:
            async for discovery in discoveries:
                print(discovery)
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[Discovery | None] = asyncio.Queue()

    async def reader() -> AsyncIterator[Discovery]:
        while True:
            item = await queue.get()
            # 'None' signals the end of discovery
            if item is None:
                break
            yield item

    @asynccontextmanager
    async def _discover() -> AsyncIterator[AsyncIterator[Discovery]]:
        handle: asyncio.TimerHandle | None = None
        if duration is not None:
            # Add 'None' to the queue to signal the end of discovery
            handle = loop.call_later(duration, queue.put_nowait, None)

        try:
            async with _discover_with_callback(queue.put_nowait, timeout=timeout):
                yield reader()
        finally:
            # Clean up timer handle if we started one
            if handle is not None:
                handle.cancel()

    return _discover()


class _Listener(ServiceListener):
    def __init__(self, callback: Callable[[Discovery], None], timeout: float) -> None:
        super().__init__()
        self._loop = asyncio.get_running_loop()
        self._timeout_ms = 1000 * timeout
        self._callback = callback
        self._tasks: list[asyncio.Task[None]] = []

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            for task in self._tasks:
                await task
            self._tasks.clear()
        finally:
            # Any tasks still pending (which could happen if we get here because of an exception)
            # are cancelled.
            for task in self._tasks:
                task.cancel()

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        if not name.startswith(_DINGZ_NAME_PREFIX):
            return
        task = self._loop.create_task(self._add_service(zc, type_, name))
        self._tasks.append(task)

    async def _add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = AsyncServiceInfo(type_, name)
        await info.async_request(zc, self._timeout_ms)
        if not info:
            _LOGGER.debug("Failed to discover %s", name)
            return
        discovery = Discovery.from_service_info(info)
        _LOGGER.debug("Discovered %s (%s)", discovery, info)
        self._callback(discovery)


@asynccontextmanager
async def _discover_with_callback(
    callback: Callable[[Discovery], None],
    *,
    timeout: float,
) -> AsyncIterator[None]:
    """Discover dingz devices with a callback.

    This function is a async context manager. While entered, it will handle zeroconf announcements
    and call the provided function with every device discovered. The callback will not be called
    again as soon as as the context manager is exited.
    """
    async with (
        AsyncZeroconf() as zc,
        _Listener(callback, timeout=timeout) as listener,
        AsyncServiceBrowser(zc.zeroconf, "_http._tcp.local.", listener=listener),
    ):
        yield

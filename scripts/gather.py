#!/usr/bin/env -S uv run
"""Gather snapshot data from a dingz device.

This data is then used for the unit tests.

Snapshots are placed in the `tests/snapshots` directory.
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, cast

import dingz.discovery
from dingz.rest import Device, RestClient
from tests.snapshot import Endpoint, Error, Snapshot

if TYPE_CHECKING:
    from collections.abc import Awaitable, Iterable

_LOGGER = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_REDACTED_VALUE = "[redacted]"


class _Args(Protocol):
    host: str | None
    scan: bool


def _parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Gather information from a dingz device.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--host",
        type=str,
        help="Hostname or IP of the device",
    )
    group.add_argument(
        "--scan",
        action="store_true",
        help="Scan for devices on the network",
    )
    args = parser.parse_args()
    return cast("_Args", args)


async def main() -> None:
    args = _parse_args()

    try:
        import colorlog  # noqa: PLC0415

        colorlog.basicConfig(level=logging.DEBUG)  # pyright: ignore[reportUnknownMemberType]
    except ImportError:
        logging.basicConfig(level=logging.DEBUG)

    hosts: set[str] = set()
    if args.scan:
        devices = await dingz.discovery.discover_list()
        hosts.update(device.host for device in devices)
    if args.host is not None:
        hosts.add(args.host)

    semaphore = asyncio.Semaphore(8)

    tasks: list[asyncio.Task[None]] = []
    for host in hosts:
        await semaphore.acquire()
        task = asyncio.create_task(_run_for_host(host, semaphore=semaphore))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def _run_for_host(host: str, *, semaphore: asyncio.Semaphore) -> None:
    try:
        async with RestClient(host) as client:
            _LOGGER.info("Gathering data from %s", host)
            snapshot = await gather_snapshot(client)
            _LOGGER.info("Done with %s. Writing to %s", host, snapshot.path())
            snapshot.save()
    finally:
        semaphore.release()


T = TypeVar("T")


async def gather_endpoint(
    fn: Callable[[], Awaitable[T]],
    *,
    name: str,
    redact_paths: Iterable[str] | None = None,
) -> Endpoint[T]:
    _LOGGER.debug("Gathering endpoint %s", name)
    try:
        value = await fn()
    except Exception as e:  # noqa: BLE001
        _LOGGER.warning("Error gathering endpoint: %s", e)
        return Endpoint(value=None, error=Error(type=str(e)))

    if redact_paths is not None:
        _redact_paths(value, redact_paths)

    return Endpoint(value=value, error=None)


def _redact_path(container: Any, path: str) -> bool:
    segments = path.split(".")
    for segment in segments[:-1]:
        if not isinstance(container, dict) or segment not in container:
            return False
        container = cast("dict[str, Any]", container)
        container = container[segment]
    key = segments[-1]
    if not (isinstance(container, dict) and key in container):
        return False
    container[key] = _REDACTED_VALUE
    return True


def _redact_paths(container: Any, paths: Iterable[str]) -> None:
    for path in paths:
        if not _redact_path(container, path):
            _LOGGER.warning("Unable to redact path %s", path)


async def gather_snapshot(client: RestClient) -> Snapshot:
    # Don't redact yet so we can generate the device hash
    device = await gather_endpoint(
        lambda: client.get_device(),
        name="device",
    )
    if device.value is None:
        device_hash = "unknown"
    else:
        device_hash = _generate_device_hash(device.value)
        _redact_paths(device.value, ["puck_sn", "front_sn"])

        # The `get_device` method contains a bit of magic that we need to revert here.
        device_data = device.value.copy()
        device_id = device_data.pop("device_id")
        device = dataclasses.replace(device, value={device_id: device_data})

    return Snapshot(
        device_hash=device_hash,
        firmware_version=await gather_endpoint(
            lambda: client.get_firmware_version(), name="firmware_version"
        ),
        device=device,
        network_info=await gather_endpoint(
            lambda: client.get_network_info(),
            name="network_info",
            redact_paths=["mac", "ssid", "ip", "mask", "gw", "dns"],
        ),
        config_dump=await gather_endpoint(
            lambda: client.get_config_dump(),
            name="config_dump",
        ),
        state=await gather_endpoint(
            lambda: client.get_state(),
            name="state",
            redact_paths=[
                "wifi.mac",
                "wifi.ssid",
                "wifi.ip",
                "wifi.mask",
                "wifi.gateway",
                "wifi.dns",
            ],
        ),
        ram=await gather_endpoint(
            lambda: client.get_ram(),
            name="ram",
            redact_paths=[],
        ),
    )


def _generate_device_hash(data: Device) -> str:
    device_hash = hashlib.sha256(usedforsecurity=False)
    try:
        front_sn: str = data["front_sn"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
    except (TypeError, KeyError):
        pass
    else:
        device_hash.update(front_sn.encode("utf-8"))

    try:
        puck_sn: str = data["puck_sn"]
    except (TypeError, KeyError):
        pass
    else:
        device_hash.update(puck_sn.encode("utf-8"))

    return device_hash.hexdigest()[:12]


if __name__ == "__main__":
    asyncio.run(main())

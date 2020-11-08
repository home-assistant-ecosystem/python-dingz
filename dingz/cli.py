"""Command-line interface to interact with dingz devices."""
import asyncio
from functools import wraps

import click

from dingz.dingz import Dingz

from .discovery import discover_dingz_devices


def coro(f):
    """Allow to use async in click."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        """Async wrapper."""
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.version_option()
def main():
    """Simple command-line tool to interact with dingz devices."""


@main.command("discover")
@coro
async def discover():
    """Read the current configuration of a myStrom device."""
    click.echo("Waiting for UDP broadcast packages...")
    devices = await discover_dingz_devices()

    print(f"Found {len(devices)} devices")
    for device in devices:
        print(
            f"  MAC address: {device.mac}, IP address: {device.host}, HW: {device.hardware}"
        )

@main.group("info")
def info():
    """Get the information of a dingz device."""


@info.command("read")
@coro
@click.option(
    "--ip", prompt="IP address of the device", help="IP address of the device."
)
async def get_config(ip):
    """Read the current configuration of a myStrom device."""
    click.echo("Read configuration from %s" % ip)
    async with Dingz(ip) as dingz:
        await dingz.get_device_info()
        click.echo(dingz.device_details)

if __name__ == "__main__":
    main()

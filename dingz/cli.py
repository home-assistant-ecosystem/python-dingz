"""Command-line interface to interact with dingz devices."""
import click
from .discovery import discover_dingz_devices
import asyncio


import asyncio
from functools import wraps


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


if __name__ == "__main__":
    main()

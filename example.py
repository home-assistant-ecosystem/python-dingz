"""Sample code to use the wrapper for interacting with the dingz device."""
import asyncio

from dingz.dingz import Dingz

IP_ADDRESS = "192.168.0.103"


async def main():
    """Sample code to work with a dingz unit."""
    async with Dingz(IP_ADDRESS) as dingz:

        # Collect the data of the current state
        await dingz.get_device_info()
        print("Device details:", dingz.device_details)

        # Get the temperature
        await dingz.get_temperature()
        print("Temperature:", dingz.temperature)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

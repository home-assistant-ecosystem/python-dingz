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

        # Turn on the front LED
        print("Turning Front LED on...")
        await dingz.turn_on()
        await asyncio.sleep(3)
        print("Front LED:", await dingz.enabled())
        await dingz.turn_off()
        print("Front LED:", await dingz.enabled())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

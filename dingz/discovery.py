import asyncio
import logging
from typing import Optional, List

_LOGGER = logging.getLogger(__name__)


class DiscoveredDevice(object):
    mac: str
    type: int
    is_child: bool
    mystrom_registered: bool
    mystrom_online: bool
    restarted: bool

    @staticmethod
    def create_from_announce_msg(raw_addr, announce_msg):
        _LOGGER.debug("received announce msg '%s' from %s ", announce_msg, raw_addr)
        if len(announce_msg) != 8:
            raise RuntimeError("unexpected announcement, '%s'" % announce_msg)

        device = DiscoveredDevice(host=raw_addr[0], mac=announce_msg[0:6].hex(":"))
        device.type = announce_msg[6]
        status = announce_msg[7]

        # parse status field
        device.is_child = status & 1 != 0
        device.mystrom_registered = status & 2 != 0
        device.mystrom_online = status & 4 != 0
        device.restarted = status & 8 != 0
        return device

    def __init__(self, host, mac):
        self.host = host
        self.mac = mac


class DeviceRegistry(object):
    def __init__(self):
        self.devices_by_mac = {}

    def register(self, device):
        self.devices_by_mac[device.mac] = device

    def devices(self):
        return list(self.devices_by_mac.values())


class DiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, registry: DeviceRegistry):
        super().__init__()
        self.registry = registry

    def connection_made(self, transport):
        _LOGGER.debug("starting up udp listener")
        self.transport = transport

    def datagram_received(self, data, addr):
        device = DiscoveredDevice.create_from_announce_msg(addr, data)
        self.registry.register(device)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        _LOGGER.debug("shutting down udp listener")
        super().connection_lost(exc)


async def discover_dingz_devices(timeout: int = 7) -> List[DiscoveredDevice]:
    """
    Try to discover all local dingz instances. All dingz instances
    report their presence every ~5 seconds in a UDP broadcast to port 7979.

    :param timeout: timeout in seconds for discover.
    :return: list of discovered devices
    """
    registry = DeviceRegistry()
    loop = asyncio.get_event_loop()
    (transport, protocol) = await loop.create_datagram_endpoint(
        lambda: DiscoveryProtocol(registry), local_addr=("0.0.0.0", 7979)
    )
    # server runs in the background, meanwhile wait until timeout expires
    await asyncio.sleep(timeout)

    # shutdown server
    transport.close()

    devices = registry.devices()
    for device in devices:
        _LOGGER.debug(
            "discovered dingz %s (%s) with mac %s", device.host, device.type, device.mac
        )
    return devices


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    devices = asyncio.run(discover_dingz_devices())

    print("found %s devices" % len(devices))
    for device in devices:
        print(f"{device.mac} {device.host}")

"""
This test ensures that the type definitions used by `dingz.rest` actually match observed API
responses.
"""

from typing import Any

from pydantic import TypeAdapter

from dingz.rest import Device, NetworkInfo, Ram, RestClient, State


def _validate_strict(ty: Any, value: Any) -> None:
    adapter = TypeAdapter(ty)
    adapter.validate_python(value)


async def test_device_type(rest_client_with_snapshot: RestClient) -> None:
    device = await rest_client_with_snapshot.get_device()
    _validate_strict(Device, device)


async def test_network_info(rest_client_with_snapshot: RestClient) -> None:
    nw_info = await rest_client_with_snapshot.get_network_info()
    _validate_strict(NetworkInfo, nw_info)


async def test_state(rest_client_with_snapshot: RestClient) -> None:
    state = await rest_client_with_snapshot.get_state()
    _validate_strict(State, state)


async def test_ram(rest_client_with_snapshot: RestClient) -> None:
    ram = await rest_client_with_snapshot.get_ram()
    _validate_strict(Ram, ram)

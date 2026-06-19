"""
This test ensures that the type definitions used by `dingz.rest` actually match observed API
responses.
"""

from typing import Any

from pydantic import TypeAdapter

from dingz.rest import (
    ActionsConfig,
    ButtonsConfig,
    ConfigDump,
    DdiConfig,
    Device,
    InputsConfig,
    LuxConfig,
    NetworkInfo,
    OutputsConfig,
    PirsConfig,
    Ram,
    RestClient,
    SchedulerConfig,
    ServicesConfig,
    State,
    SystemConfig,
)


def _validate_strict(ty: Any, value: Any) -> None:
    adapter = TypeAdapter(ty)
    adapter.validate_python(value)


async def test_device(rest_client_with_snapshot: RestClient) -> None:
    device = await rest_client_with_snapshot.get_device()
    _validate_strict(Device, device)


async def test_network_info(rest_client_with_snapshot: RestClient) -> None:
    nw_info = await rest_client_with_snapshot.get_network_info()
    _validate_strict(NetworkInfo, nw_info)


async def test_config_dump(rest_client_with_snapshot: RestClient) -> None:
    config_dump = await rest_client_with_snapshot.get_config_dump()
    _validate_strict(ConfigDump, config_dump)


async def test_state(rest_client_with_snapshot: RestClient) -> None:
    state = await rest_client_with_snapshot.get_state()
    _validate_strict(State, state)


async def test_ram(rest_client_with_snapshot: RestClient) -> None:
    ram = await rest_client_with_snapshot.get_ram()
    _validate_strict(Ram, ram)


async def test_button_config(rest_client_with_snapshot: RestClient) -> None:
    button_config = await rest_client_with_snapshot.get_button_config()
    _validate_strict(ButtonsConfig, button_config)


async def test_input_config(rest_client_with_snapshot: RestClient) -> None:
    input_config = await rest_client_with_snapshot.get_input_config()
    _validate_strict(InputsConfig, input_config)


async def test_pir_config(rest_client_with_snapshot: RestClient) -> None:
    pir_config = await rest_client_with_snapshot.get_pir_config()
    _validate_strict(PirsConfig, pir_config)


async def test_lux_config(rest_client_with_snapshot: RestClient) -> None:
    lux_config = await rest_client_with_snapshot.get_lux_config()
    _validate_strict(LuxConfig, lux_config)


async def test_output_config(rest_client_with_snapshot: RestClient) -> None:
    output_config = await rest_client_with_snapshot.get_output_config()
    _validate_strict(OutputsConfig, output_config)


async def test_services_config(rest_client_with_snapshot: RestClient) -> None:
    services_config = await rest_client_with_snapshot.get_services_config()
    _validate_strict(ServicesConfig, services_config)


async def test_system_config(rest_client_with_snapshot: RestClient) -> None:
    system_config = await rest_client_with_snapshot.get_system_config()
    _validate_strict(SystemConfig, system_config)


async def test_ddi_config(rest_client_with_snapshot: RestClient) -> None:
    ddi_config = await rest_client_with_snapshot.get_ddi_config()
    _validate_strict(DdiConfig, ddi_config)


async def test_actions_config(rest_client_with_snapshot: RestClient) -> None:
    actions_config = await rest_client_with_snapshot.get_actions_config()
    _validate_strict(ActionsConfig, actions_config)


async def test_scheduler_config(rest_client_with_snapshot: RestClient) -> None:
    scheduler_config = await rest_client_with_snapshot.get_scheduler_config()
    _validate_strict(list[SchedulerConfig], scheduler_config)

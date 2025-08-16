from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = [
    "BlindState",
    "CloudState",
    "ConfigState",
    "DdiChannelState",
    "DimmerState",
    "DynLightState",
    "LedState",
    "LightState",
    "PirSensorState",
    "PowerOutputSensorState",
    "SensorsState",
    "State",
    "ThermostatState",
    "WifiState",
]

LightState = Literal["day", "twilight", "night"]


class _Index(TypedDict):
    """Index information of a dingz sub-component."""

    relative: int
    """The relative index of dimmer (depending on DIP switch configuration).

    Use this index to refer to component for actions.
    """
    absolute: int
    """The absolute index. Refers to hardware output number."""


class DimmerState(TypedDict):
    """Dimmer status part of `State`."""

    on: bool
    """Dimmer status, on/off"""
    output: int
    """The dim value set on dimmer. This value is "0" if `on` is false."""
    ramp: int
    """The ramp (how quickly change dim value) set on dimmer.

    The ramp is always 0 for non dimmable outputs.
    """
    readonly: bool
    """Whether the dimmer is disabled or not."""
    off_timer_type: Literal["none", "pir"]  # TODO: incomplete
    off_timer_id: int
    off_timer_value: int
    index: _Index


# TODO CHECK
class BlindState(TypedDict):
    """Blind status part of `State`."""

    moving: Literal["up", "down", "stop"]
    position: int
    """closed = 0, open = 100"""
    lamella: int
    """closed = 0, open = 100"""
    readonly: bool
    index: _Index


# TODO CHECK
class DdiChannelState(TypedDict):
    """DDI Channel status part of `State`."""

    name: str
    en: bool
    on: bool
    brightness: int
    ct_enabled: bool
    colour_temperature: int
    colour_temperature_k: int
    off_timer_type: str
    off_timer_id: int
    off_timer_value: int


class LedState(TypedDict):
    """LED status part of `State`."""

    on: bool
    """Whether or not the LED is on."""
    hsv: str
    rgb: str
    mode: Literal["hsv", "rgb"]
    """Color format used by LED."""
    ramp: int
    """Defines ramp/fade speed of color change (change from previous to new value).

    Range: `[0, 102375]`
    """
    override_level: int


class PirSensorState(TypedDict):
    """PIR sensor status part of `SensorsState`."""

    enabled: bool
    motion: bool
    mode: Literal["auto", "idle"]  # TODO: INCOMPLETE
    light_off_timer: int
    suspend_timer: int


class PowerOutputSensorState(TypedDict):
    """Power output sensor status part of `SensorsState`."""

    value: float


class SensorsState(TypedDict):
    """Sensors status part of `State`."""

    brightness: int
    light_state: LightState
    light_state_lpf: LightState
    room_temperature: float
    uncompensated_temperature: float
    temp_offset: float
    cpu_temperature: float
    puck_temperature: float
    fet_temperature: float
    input_state: bool | None
    pirs: list[PirSensorState | None]
    """PIR sensor states.

    Only the first value seems to be relevant.
    The first value will be `None` if the device does not have a PIR sensor.
    """
    power_outputs: list[PowerOutputSensorState]


class DynLightState(TypedDict):
    """Dyn light status part of `State`."""

    mode: LightState


class ThermostatState(TypedDict):
    """Thermostat status part of `State`."""

    active: bool
    state: Literal["off"]  # TODO: incomplete
    mode: Literal["off"]  # TODO: incomplete
    user_mode: Literal["comfort"]  # TODO: incomplete
    enabled: bool
    target_temp: int
    min_target_temp: int
    max_target_temp: int
    cooling: bool
    free_cooling: bool
    temp: float


class WifiState(TypedDict):
    """Wifi status part of `State`."""

    version: str
    mac: str
    ssid: str
    ip: str
    mask: str
    gateway: str
    dns: str
    static: bool
    connected: bool


class CloudState(TypedDict):
    """Cloud status part of `State`."""

    aws: Literal["connected", "disconnected"]  # TODO: incomplete


class ConfigState(TypedDict):
    """Config status part of `State`."""

    timestamp: int


class State(TypedDict):
    """Full device status returned by the `/api/v1/state` endpoint."""

    dimmers: list[DimmerState]
    blinds: list[BlindState]
    ddi_channels: list[DdiChannelState]
    led: LedState
    sensors: SensorsState
    dyn_light: DynLightState
    thermostat: ThermostatState
    wifi: WifiState
    cloud: CloudState
    time: str
    config: ConfigState

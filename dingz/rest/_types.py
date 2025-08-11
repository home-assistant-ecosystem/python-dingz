from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired, TypedDict


class Index(TypedDict, total=True):
    """Index information of a dingz sub-component."""

    relative: int
    """The relative index of dimmer (depending on DIP switch configuration).

    Use this index to refer to component for actions.
    """
    absolute: int
    """The absolute index. Refers to hardware output number."""


LightState = Literal["day", "twilight", "night"]


class Date(TypedDict, total=True):
    """Split date information part of `Device`."""

    year: int
    month: int
    day: int


class Device(TypedDict, total=True):
    """Device information returned by the `/api/v1/device` endpoint."""

    type: Literal["dingz"]
    device_id: str
    """User-settable identifier of the device.

    This field isn't present in the API model itself. The actual API response is a
    `dict[str, Device]` with a single entry. The key is the device id.
    """
    battery: bool
    reachable: bool
    meshroot: bool
    fw_version: str
    hw_version: str
    fw_version_puck: str
    bl_version_puck: str
    hw_version_puck: str
    hw_id_puck: int
    puck_sn: str
    puck_production_date: Date
    ddi_base: bool
    dip_config: int
    dip_static: bool
    dip_misconf: bool
    puck_hw_model: Literal["DZ1B-4CH", ""]  # TODO: incomplete
    """Puck hardware model.

    Can be an empty string if unknown.
    """
    front_hw_model: NotRequired[Literal["dz1f-pir", "dz1f-4b"]]  # TODO: incomplete
    """Front hardware model.

    Can be missing.
    """
    front_production_date: NotRequired[str]
    """Front production date.

    Format: `DD/MM/YY`

    Can be missing.
    """
    front_sn: NotRequired[str]
    """Front serial number.

    Can be missing.
    """
    front_color: str
    has_pir: bool
    first_boot: bool
    hash: str


class NetworkInfo(TypedDict, total=True):
    """Network information returned by the `/api/v1/info` endpoint."""

    version: str
    """Version of the front."""
    mac: str
    """MAC Address"""
    type: Literal[108]  # TODO: incomplete?
    ssid: str
    ip: str
    mask: str
    gw: str
    dns: str
    static: bool
    connected: bool


class DimmerState(TypedDict, total=True):
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
    index: Index


# TODO CHECK
class BlindState(TypedDict, total=True):
    """Blind status part of `State`."""

    moving: Literal["up", "down", "stop"]
    position: int
    """closed = 0, open = 100"""
    lamella: int
    """closed = 0, open = 100"""
    readonly: bool
    index: Index


# TODO CHECK
class DdiChannelState(TypedDict, total=True):
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


class LedState(TypedDict, total=True):
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


class PirSensorState(TypedDict, total=True):
    """PIR sensor status part of `SensorsState`."""

    enabled: bool
    motion: bool
    mode: Literal["idle"]  # TODO: INCOMPLETE
    light_off_timer: int
    suspend_timer: int


class PowerOutputSensorState(TypedDict, total=True):
    """Power output sensor status part of `SensorsState`."""

    value: float


class SensorsState(TypedDict, total=True):
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


class DynLightState(TypedDict, total=True):
    """Dyn light status part of `State`."""

    mode: LightState


class ThermostatState(TypedDict, total=True):
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


class WifiState(TypedDict, total=True):
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


class CloudState(TypedDict, total=True):
    """Cloud status part of `State`."""

    aws: Literal["connected", "disconnected"]  # TODO: incomplete


class ConfigState(TypedDict, total=True):
    """Config status part of `State`."""

    timestamp: int


class State(TypedDict, total=True):
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

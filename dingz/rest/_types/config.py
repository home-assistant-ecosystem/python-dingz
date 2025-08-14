from __future__ import annotations

from typing_extensions import Literal, NotRequired, TypedDict

# We need to actually import these types for `pydantic.TypeAdapter` to work.
from .helpers import Color  # noqa: TC001

__all__ = [
    "ActionsConfig",
    "BlindConfig",
    "BlindsConfig",
    "ButtonConfig",
    "ButtonsConfig",
    "ConfigDump",
    "DdiChannelConfig",
    "DdiChannelsConfig",
    "DdiConfig",
    "InputConfig",
    "InputsConfig",
    "LedConfig",
    "LuxConfig",
    "NlConfig",
    "OutputConfig",
    "OutputsConfig",
    "OutputsConfig",
    "PirConfig",
    "PirsConfig",
    "SchedulerConfig",
    "ServicesConfig",
    "SystemConfig",
    "ThermostatConfig",
]


class _LocalAndRemote(TypedDict):
    local: bool
    remote: bool


class _LightAndMotor(TypedDict):
    light: bool
    motor: bool


class _Actions(TypedDict):
    off: bool
    default_on: bool
    custom_on: bool
    open: bool
    close: bool
    default_pos: bool
    custom_pos: bool


class _DdiActions(TypedDict):
    brightness: bool
    colour_temperature: bool


class _OutputsLocalCustom(TypedDict):
    value: int


class _OutputsLocal(TypedDict):
    controlled: bool
    custom: _OutputsLocalCustom


class _OutputsRemoteCustom(TypedDict):
    value: int
    ct_value: int


class _OutputsRemote(TypedDict):
    groups: str
    custom: _OutputsRemoteCustom


class _OutputsDdiControlled(TypedDict):
    active: bool
    channel_id: int


class _OutputsDdiCustom(TypedDict):
    brightness: int
    colour_temperature: int


class _OutputsDdi(TypedDict):
    controlled: _OutputsDdiControlled
    custom: _OutputsDdiCustom


class _Outputs(TypedDict):
    fade_in_time: int
    fade_out_time: int
    auto_off_delay: int
    local: list[_OutputsLocal]
    remote: _OutputsRemote
    ddi: _OutputsDdi


class _BlindAndLamella(TypedDict):
    blind: int
    lamella: int


class _MotorsLocal(TypedDict):
    controlled: bool
    custom: _BlindAndLamella


class _MotorsRemote(TypedDict):
    groups: str
    custom: _BlindAndLamella


class _Motors(TypedDict):
    invert: bool
    local: list[_MotorsLocal]
    remote: _MotorsRemote


class _Feedback(TypedDict):
    color: Literal["none"] | Color
    brightness: int


class _ActionTriggerBase(TypedDict):
    active: bool
    name: str
    icon: int
    mode: _LocalAndRemote
    local_type: _LightAndMotor
    type: _LightAndMotor
    actions: _Actions
    ddi_actions: _DdiActions
    outputs: _Outputs
    motors: _Motors
    feedback: _Feedback
    carousel: bool


class _Button(TypedDict):
    remote_push: bool
    therm_ctrl: bool


class ButtonConfig(_ActionTriggerBase):
    """Button configuration part of `ButtonsConfig`."""

    button: _Button


class ButtonsConfig(TypedDict):
    """Button config returned by the `/api/v1/button_config` endpoint."""

    dingz_orientation: str
    """Dingz orientation (e.g. '1,2,3,4')."""
    buttons: list[ButtonConfig]


class _InputConfigContactFreeCooling(TypedDict):
    repeat_period: int


class _InputConfigInput(TypedDict):
    type: Literal["button_toggle", "button_push", "contact_state"]
    invert: bool
    contact_free_cooling: _InputConfigContactFreeCooling


class InputConfig(_ActionTriggerBase):
    """Button configuration part of `InputsConfig`."""

    input: _InputConfigInput


class InputsConfig(TypedDict):
    """Inputs config returned by the `/api/v1/input_config` endpoint."""

    inputs: list[InputConfig]


class _PirConfigPir(TypedDict):
    backoff_time: int
    on_time: int
    manual_on_time: int
    manual_off_time: int


class PirConfig(_ActionTriggerBase):
    """PIR configuration part of `PirsConfig`."""

    pir: _PirConfigPir


class PirsConfig(TypedDict):
    """PIR config returned by the `/api/v1/pir_config` endpoint."""

    pirs: list[PirConfig]


class _LuxConfigThresholds(TypedDict):
    twilight_to_night: int
    night_to_twilight: int
    day_to_twilight: int
    twilight_to_day: int
    day_to_night: int
    night_to_day: int


class LuxConfig(TypedDict):
    """Lux config returned by the `/api/v1/lux_config` endpoint."""

    enabled: bool
    output: None
    ddi_channels: None
    feedback: bool
    dim_value_night: int
    dim_value_twilight: int
    dim_value_day: int
    ct_value_night: int
    ct_value_twilight: int
    ct_value_day: int
    fade_in_time: int
    fade_out_time: int
    thresholds: _LuxConfigThresholds
    light_lpf: bool
    off_period: int


class _ThermostatFeedback(TypedDict):
    enable: bool
    brightness: int


class _ThermostatOutput(TypedDict):
    controlled: bool


class ThermostatConfig(TypedDict):
    """Thermostat config returned by the `/api/v1/thermostat_config` endpoint."""

    active: bool
    min_target_temp: int
    max_target_temp: int
    target_temp: int
    cooling: bool
    enable: bool
    fahrenheit: bool
    free_cooling: bool
    groups: str
    mode: _LocalAndRemote
    feedback: _ThermostatFeedback
    outputs: list[_ThermostatOutput]
    user_mode: Literal["comfort"]


class LedConfig(TypedDict):
    """LED config returned by the `/api/v1/led_config` endpoint."""

    state: bool
    local_feedback: bool
    groups: str


class _Range(TypedDict):
    min: int
    max: int


class _Dynamic(TypedDict):
    day: int
    twilight: int
    night: int


class _LightDimmer(TypedDict):
    type: Literal["led_driver", "linear", "led_bulb", "halogen_bulb"]
    use_last_value: bool
    range: _Range
    dynamic: _Dynamic


class _LightOnoffGroupOn(TypedDict):
    day: bool
    twilight: bool
    night: bool


class _LightOnoff(TypedDict):
    group_on: _LightOnoffGroupOn


class _Light(TypedDict):
    dimmable: bool
    auto_off_delay: int
    dimmer: _LightDimmer
    onoff: _LightOnoff


class _Heater(TypedDict):
    type: Literal["nc"]
    function: Literal["heating"]


class _PulseLength(TypedDict):
    min: float
    max: float


class _Pulse(TypedDict):
    type: Literal["positive"]
    length: _PulseLength


class _FanDelay(TypedDict):
    pre: int
    post: int


class _HourAndMinute(TypedDict):
    hour: int
    minute: int


_FanVentilation = TypedDict(
    "_FanVentilation",
    {
        "from": _HourAndMinute,
        "to": _HourAndMinute,
        "force_in_24": int,
    },
)


class _FanReact(TypedDict):
    pir_during_slot: bool
    btn_no_delay: bool


class _Fan(TypedDict):
    delay: _FanDelay
    ventilation: _FanVentilation
    react: _FanReact
    active: bool


class _GarageDoor(TypedDict):
    opening_travel_time: int
    close_timeout: int
    pulse_time: int


class _Valve(TypedDict):
    duration: int


class OutputConfig(TypedDict):
    """Output configuration part of `OutputsConfig`."""

    active: bool
    name: str
    type: Literal["light"]
    groups: str
    feedback: _Feedback
    light: _Light
    heater: _Heater
    pulse: _Pulse
    fan: _Fan
    garage_door: _GarageDoor
    valve: _Valve


class OutputsConfig(TypedDict):
    """Outputs config returned by the `/api/v1/output_config` endpoint."""

    outputs: list[OutputConfig]


class BlindConfig(TypedDict):
    """Blind configuration part of `BlindsConfig`."""

    active: bool
    name: str
    type: Literal["blind"]
    min_value: int
    max_value: int
    def_blind: int
    def_lamella: int
    groups: str
    auto_calibration: bool
    shade_up_time: int
    shade_down_time: int
    invert_direction: bool
    lamella_time: float
    step_duration: int
    step_interval: int
    state: Literal["Not initialised"]


class BlindsConfig(TypedDict):
    """Blinds config returned by the `/api/v1/blind_config` endpoint."""

    blinds: list[BlindConfig]


_ServicesConfigMqtt = TypedDict(
    "_ServicesConfigMqtt",
    {
        "uri": str,
        "enable": bool,
        "server.crt": "str | None",
    },
)


class ServicesConfig(TypedDict):
    """Services config returned by the `/api/v1/services_config` endpoint."""

    mystrom: bool
    homekit: bool
    panel: bool
    aws: bool
    discovery: bool
    udp_search: bool
    aws_notifies: bool
    ssdp: bool
    mdns: bool
    mdns_search: bool
    homekit_configured: bool
    cloud_ping: bool
    broadcast_period: int
    mdns_search_period: int
    mqtt: _ServicesConfigMqtt
    cloud_paired: bool
    cloud_test_enabled: bool


class _SystemConfigTempComp(TypedDict):
    fet_offset: float
    gain_up: float
    gain_down: float
    gain_total: float
    idle_offset: int
    front_offset: int
    inf_factor: float


class _SystemConfigDynLightSunOffset(TypedDict):
    day: int
    twilight: int
    night: int


class _SystemConfigDynLight(TypedDict):
    enable: bool
    phases: int
    source: Literal["sun", "lux"]
    sun_offset: _SystemConfigDynLightSunOffset


class SystemConfig(TypedDict):
    """System config returned by the `/api/v1/system_config` endpoint."""

    rest_password: bool
    protected_status: bool
    allow_reset: bool
    allow_wps: bool
    allow_reboot: bool
    allow_remote_reboot: bool
    allow_update: bool
    origin: bool
    upgrade_blink: bool
    reboot_blink: bool
    dingz_name: str
    room_name: str
    home_name: str
    id: str
    temp_offset: float
    fet_offset: NotRequired[float]
    cpu_offset: NotRequired[float]
    temp_comp: _SystemConfigTempComp
    sun_offset: int
    tzid: int
    lat: float
    long: float
    dyn_light: _SystemConfigDynLight
    wifi_ps: bool
    new_comp_alg: bool


class DdiConfig(TypedDict):
    """DDI config returned by the `/api/v1/ddi_config` endpoint."""

    repeat: bool
    repeat_interval: int


class _DdiChannelConfigFeaturesColourTemperature(TypedDict):
    en: bool
    range: _Range
    dynamic: _Dynamic


class _DdiChannelConfigFeatures(TypedDict):
    colour_temperature: _DdiChannelConfigFeaturesColourTemperature


class DdiChannelConfig(TypedDict):
    """DDI channel configuration part of `DdiChannelsConfig`."""

    name: str
    en: bool
    ddi_group_id: int
    dingz_groups: str
    use_last_value: bool
    auto_off_delay: int
    range: _Range
    dynamic: _Dynamic
    features: _DdiChannelConfigFeatures
    feedback: _Feedback


class DdiChannelsConfig(TypedDict):
    """DDI channels config returned by the `/api/v1/ddi_channels_config` endpoint."""

    ddi_channels: list[DdiChannelConfig]


class _NlConfigLed(TypedDict):
    color: str
    """Semicolon-separated RGB color code (e.g. "255;0;0" for red)."""


# TODO: what even is this??
class NlConfig(TypedDict):
    enable: bool
    on: _HourAndMinute
    off: _HourAndMinute
    dimmers: list[None]
    ddi_channels: list[None]
    led: _NlConfigLed | None


class _ActionsConfigBtnFeedback(TypedDict):
    single: bool
    double: bool
    long: bool
    m3: bool
    m4: bool
    m5: bool
    begin: bool
    hold_up: bool
    hold_down: bool
    end: bool
    off: bool


class _ActionsConfigBase(TypedDict):
    single: str
    double: str
    long: str
    m3: str
    m4: str
    m5: str
    begin: str
    hold_up: str
    hold_down: str
    end: str
    off: str
    hold_up_repeat_period: int
    hold_down_repeat_period: int


class _ActionsConfigBtn(_ActionsConfigBase):
    feedback: _ActionsConfigBtnFeedback


class _ActionsConfigInputFeedback(_ActionsConfigBtnFeedback):
    active: bool
    inactive: bool


class _ActionsConfigInput(_ActionsConfigBase):
    active: str
    inactive: str
    active_repeat_period: int
    inactive_repeat_period: int
    feedback: _ActionsConfigInputFeedback


class _ActionsConfigThermostat(TypedDict):
    idle: str
    heating: str
    cooling: str
    repeat_period: int


class _ActionsConfigLux(TypedDict):
    night: str
    twilight: str
    day: str
    repeat_period: int


class _ActionsConfigPirFeedback(TypedDict):
    night: bool
    twilight: bool
    day: bool
    rise: bool
    fall: bool
    timer_off: bool


class _ActionsConfigPir(TypedDict):
    night: str
    twilight: str
    day: str
    rise: str
    fall: str
    timer_off: str
    motion_repeat_period: int
    feedback: _ActionsConfigPirFeedback


class ActionsConfig(TypedDict):
    """Actions config returned by the `/api/v1/action` endpoint."""

    generic: str
    btn1: _ActionsConfigBtn
    btn2: _ActionsConfigBtn
    btn3: _ActionsConfigBtn
    btn4: _ActionsConfigBtn
    input: _ActionsConfigInput
    input2: _ActionsConfigInput
    thermostat: _ActionsConfigThermostat
    lux: _ActionsConfigLux
    pir1: _ActionsConfigPir
    pir2: _ActionsConfigPir
    pir3: _ActionsConfigPir


class _SchedulerConfigBcEventsLightsConfigActions(TypedDict):
    off: bool
    default_on: bool
    custom_on: bool


class _SchedulerConfigBcEventsLightsConfig(TypedDict):
    fade_in_time: int
    fade_out_time: int
    groups: str
    custom_value: int
    actions: _SchedulerConfigBcEventsLightsConfigActions


class _SchedulerConfigBcEventsMotorsConfigActions(TypedDict):
    open: bool
    close: bool
    default_pos: bool
    custom_pos: bool


class _SchedulerConfigBcEventsMotorsConfig(TypedDict):
    groups: str
    shade_position: _BlindAndLamella
    actions: _SchedulerConfigBcEventsMotorsConfigActions


class _SchedulerConfigBcEvents(TypedDict):
    remote_type: _LightAndMotor
    lights_config: _SchedulerConfigBcEventsLightsConfig
    motors_config: _SchedulerConfigBcEventsMotorsConfig


class SchedulerConfig(TypedDict):
    """Scheduler config returned by the `/api/v1/scheduler` endpoint."""

    id: int
    name: str
    en: bool
    type: Literal["time"]
    hour: int
    min: int
    offset: int
    rand: int
    days: str
    url: str
    bc_events: _SchedulerConfigBcEvents


class ConfigDump(TypedDict):
    """Full config dump returned by the `/api/v1/dump_config` endpoint."""

    buttons: ButtonsConfig
    inputs: InputsConfig
    pir: PirsConfig
    lux: LuxConfig
    thermostat: ThermostatConfig
    led: LedConfig
    outputs: OutputsConfig
    blinds: BlindsConfig
    services: ServicesConfig
    system: SystemConfig
    ddi: DdiConfig
    ddi_channels: DdiChannelsConfig
    nl: NlConfig
    actions: ActionsConfig
    scheduler: list[SchedulerConfig]

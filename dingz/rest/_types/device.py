from __future__ import annotations

from typing_extensions import Literal, NotRequired, TypedDict

# We need to actually import these types for `pydantic.TypeAdapter` to work.
from .helpers import Date, ShortColorCode  # noqa: TC001

__all__ = [
    "Device",
    "NetworkInfo",
    "Ram",
]


class Device(TypedDict):
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
    front_color: ShortColorCode
    has_pir: bool
    first_boot: bool
    hash: str


class NetworkInfo(TypedDict):
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


class Ram(TypedDict):
    """RAM information returned by the `/api/v1/ram` endpoint."""

    free: int
    largest_free_block: int

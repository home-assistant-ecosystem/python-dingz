from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from typing_extensions import Self

if TYPE_CHECKING:
    from collections.abc import Mapping

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
        SchedulerConfig,
        ServicesConfig,
        State,
        SystemConfig,
    )

__all__ = [
    "REDACTED_VALUE",
    "Endpoint",
    "Error",
    "Snapshot",
]

REDACTED_VALUE = "[redacted]"


_TESTS_DIR = Path(__file__).parent
_SNAPSHOTS_DIR = _TESTS_DIR / "snapshots"


@dataclasses.dataclass(frozen=True)
class Error:
    type: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        return cls(
            type=data["type"],
        )


T = TypeVar("T")


@dataclasses.dataclass(frozen=True)
class Endpoint(Generic[T]):
    value: T | None
    error: Error | None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Endpoint[Any]:
        error_raw = data.get("error")
        error = Error.from_dict(error_raw) if error_raw else None
        return cls(
            value=data.get("value"),
            error=error,
        )


@dataclasses.dataclass(frozen=True)
class Snapshot:
    device_hash: str
    firmware_version: Endpoint[str]
    device: Endpoint[Device]
    network_info: Endpoint[NetworkInfo]
    config_dump: Endpoint[ConfigDump]
    state: Endpoint[State]
    ram: Endpoint[Ram]
    button_config: Endpoint[ButtonsConfig]
    input_config: Endpoint[InputsConfig]
    pir_config: Endpoint[PirsConfig]
    lux_config: Endpoint[LuxConfig]
    output_config: Endpoint[OutputsConfig]
    services_config: Endpoint[ServicesConfig]
    system_config: Endpoint[SystemConfig]
    ddi_config: Endpoint[DdiConfig]
    actions_config: Endpoint[ActionsConfig]
    scheduler_config: Endpoint[list[SchedulerConfig]]

    def endpoint_by_path(self, path: str) -> Endpoint[Any]:
        attr = _ENDPOINT_ATTR_MAP.get(path)
        if not attr:
            msg = f"Unknown endpoint path: {path}"
            raise LookupError(msg)
        return getattr(self, attr)

    def path(self) -> Path:
        return _SNAPSHOTS_DIR / f"{self.device_hash}.json"

    def save(self, *, force_update: bool = False) -> None:
        data = dataclasses.asdict(self)
        path = self.path()
        if not force_update and path.exists():
            old_data = json.loads(path.read_text(encoding="utf-8"))
            data = _preserve_old_value(old_data, data)

        text = json.dumps(data, indent=2)
        path.write_text(text, encoding="utf-8")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        kwargs: dict[str, Endpoint[Any]] = {}
        for attr in _ENDPOINT_ATTR_MAP.values():
            kwargs[attr] = Endpoint.from_dict(data[attr])
        return cls(device_hash=data["device_hash"], **kwargs)


_ENDPOINT_ATTR_MAP: dict[str, str] = {
    "/api/v1/firmware": "firmware_version",
    "/api/v1/device": "device",
    "/api/v1/info": "network_info",
    "/api/v1/dump_config": "config_dump",
    "/api/v1/state": "state",
    "/api/v1/ram": "ram",
    "/api/v1/button_config": "button_config",
    "/api/v1/input_config": "input_config",
    "/api/v1/pir_config": "pir_config",
    "/api/v1/lux_config": "lux_config",
    "/api/v1/output_config": "output_config",
    "/api/v1/services_config": "services_config",
    "/api/v1/system_config": "system_config",
    "/api/v1/ddi_config": "ddi_config",
    "/api/v1/action": "actions_config",
    "/api/v1/scheduler": "scheduler_config",
}


def load_snapshots() -> list[Snapshot]:
    snapshots: list[Snapshot] = []
    for path in _SNAPSHOTS_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        snapshots.append(Snapshot.from_dict(data))
    return snapshots


def _preserve_old_value(old: Any, new: Any) -> Any:  # noqa: PLR0911
    """Recursively preserve old values if they haven't changed type or meaning."""
    if isinstance(old, float) and isinstance(new, int):
        # Value changed from float to int. The API returns ints if the value happens to align.
        return old
    if type(old) is not type(new):
        return new
    if isinstance(old, dict):
        old = cast("dict[Any, Any]", old)
        new_dict = new.copy()
        for key, old_value in old.items():
            if key not in new_dict:
                continue
            new_value = new_dict[key]
            new_dict[key] = _preserve_old_value(old_value, new_value)
        return new_dict
    if isinstance(old, list):
        old = cast("list[Any]", old)
        if len(old) != len(new):
            return new
        return [_preserve_old_value(old_item, new_item) for old_item, new_item in zip(old, new)]

    if new == REDACTED_VALUE:
        # Always use the redacted value even if old wasn't yet
        return REDACTED_VALUE

    if (new == "") != (old == ""):
        # We changed from empty to non-empty string or vice versa
        return new

    return old

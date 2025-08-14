from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from typing_extensions import Self

if TYPE_CHECKING:
    from collections.abc import Mapping

    from dingz.rest import ConfigDump, Device, NetworkInfo, Ram, State

__all__ = [
    "Endpoint",
    "Error",
    "Snapshot",
]

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

    def endpoint_by_path(self, path: str) -> Endpoint[Any]:
        if path == "/api/v1/device":
            return self.device
        if path == "/api/v1/info":
            return self.network_info
        if path == "/api/v1/dump_config":
            return self.config_dump
        if path == "/api/v1/state":
            return self.state
        if path == "/api/v1/ram":
            return self.ram
        msg = f"Unknown endpoint path: {path}"
        raise LookupError(msg)

    def path(self) -> Path:
        return _SNAPSHOTS_DIR / f"{self.device_hash}.json"

    def save(self) -> None:
        text = json.dumps(dataclasses.asdict(self), indent=2)
        self.path().write_text(text, encoding="utf-8")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        return cls(
            device_hash=data["device_hash"],
            firmware_version=Endpoint.from_dict(data["firmware_version"]),
            device=Endpoint.from_dict(data["device"]),
            network_info=Endpoint.from_dict(data["network_info"]),
            config_dump=Endpoint.from_dict(data["config_dump"]),
            state=Endpoint.from_dict(data["state"]),
            ram=Endpoint.from_dict(data["ram"]),
        )


def load_snapshots() -> list[Snapshot]:
    snapshots: list[Snapshot] = []
    for path in _SNAPSHOTS_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        snapshots.append(Snapshot.from_dict(data))
    return snapshots

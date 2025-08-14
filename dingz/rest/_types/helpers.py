from typing_extensions import Literal, TypedDict

__all__ = [
    "Color",
    "Date",
    "Index",
    "ShortColorCode",
]

ShortColorCode = Literal["WH", "MC"]
Color = Literal["red", "blue", "green", "white"]


class Index(TypedDict):
    """Index information of a dingz sub-component."""

    relative: int
    """The relative index of dimmer (depending on DIP switch configuration).

    Use this index to refer to component for actions.
    """
    absolute: int
    """The absolute index. Refers to hardware output number."""


class Date(TypedDict):
    """Split date information part of `Device`."""

    year: int
    month: int
    day: int

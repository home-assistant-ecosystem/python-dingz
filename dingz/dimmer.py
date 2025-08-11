from yarl import URL

from dingz import make_call
from dingz.constants import DIMMER
from dingz.registry import BaseRegistry, organize_by_absolute_index


class Dimmer:
    def __init__(self, absolute_index, dingz) -> None:
        self.dingz = dingz
        self.absolute_index = absolute_index
        self.on = None
        self.brightness_pct = None
        self.enabled = None
        self.dimmable = None
        self.output = None
        self.name = None
        self.seen_state = False

    async def toggle(self, brightness_pct=100) -> None:
        """
        Toggle light (based on internal state).
        :param brightness_pct: brightness in percent, or None
        :return:
        """
        action = "off" if self.on else "on"
        await self.operate_light(action, brightness_pct)

    async def turn_on(self, brightness_pct=100) -> None:
        """Turn light on.
        :param brightness_pct: brightness in percent, or None.
        """
        await self.operate_light("on", brightness_pct)

    async def turn_off(self) -> None:
        """Rurn light off."""
        await self.operate_light("off")

    VALID_OPERATIONS = ("on", "off")

    async def operate_light(self, action, brightness_pct=None) -> None:
        """
        Operate the light (turn it on or off).
        :param action: 'on' or 'off'
        :param brightness_pct: brightness in percent or None if not defined
        :return:
        """
        if action not in Dimmer.VALID_OPERATIONS:
            msg = f"invalid action {action!r}, expected one of {Dimmer.VALID_OPERATIONS!r}"
            raise ValueError(msg)

        if brightness_pct is not None and (brightness_pct > 100 or brightness_pct < 0):
            msg = f"invalid brightness_pct {brightness_pct!r}, expected value between 0 and 100"
            raise ValueError(msg)

        url = URL(self.dingz.uri).join(URL(f"{DIMMER}/{self.index_relative}/{action}"))
        params = {}
        if brightness_pct is not None:
            params["value"] = str(brightness_pct)

        await make_call(self.dingz, uri=url, method="POST", parameters=params)
        self.on = action
        if brightness_pct is not None:
            self.brightness_pct = brightness_pct

    def _consume_state(self, state_details) -> None:
        """
            Example for state_details:
            {
              "on": true, "output": 100, "ramp": 0, "readonly": false,
              "index": { "relative": 0, "absolute": 2 }
            }
        :param state_details:
        :return:
        """
        assert self.absolute_index == state_details["index"]["absolute"]
        self.seen_state = True
        self.index_relative = state_details["index"]["relative"]
        self.on = state_details["on"]
        self.brightness_pct = state_details["output"]

    def _consume_config(self, config) -> None:
        # "output": "halogen", "name": "Dimmable 3", "feedback": null, "feedback_intensity": 10
        self.output = config["output"]
        self.enabled = config["output"] != "not_connected"
        self.dimmable = config["output"] != "non_dimmable"
        self.name = config["name"]


class DimmerRegistry(BaseRegistry[Dimmer]):
    def __init__(self, dingz) -> None:
        super().__init__(factory=lambda absolute_index: Dimmer(absolute_index, dingz))

    def _consume_config(self, dimmer_configs) -> None:
        for absolute_index, dimmer_config in enumerate(dimmer_configs):
            dimmer = self._get_or_create(absolute_index)
            dimmer._consume_config(dimmer_config)

    def _consume_dimmer_state(self, dimmer_states) -> None:
        for absolute_index, dimmer_state in organize_by_absolute_index(dimmer_states):
            dimmer = self._get_or_create(absolute_index)
            dimmer._consume_state(dimmer_state)

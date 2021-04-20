from yarl import URL

from dingz import make_call

from .constants import (
    SHADE
)
from .registry import BaseRegistry, organize_by_absolute_index


class Shade(object):
    def __init__(self, absolute_index, dingz):
        self.absolute_index = absolute_index
        self.dingz = dingz
        self.name = None
        self.seen_state = False
        self.moving = None
        self.position = None
        self.lamella = None

    def _consume_config(self, config):
        self.name = config['name']

    def _consume_device_state(self, state_details):
        """
        Update internal state based on server respnose.
        Eaxmple for state_details: {
              'moving': 'stop', 'position': 0, 'lamella': 0, 'readonly': False,
              'index': { 'relative': 0, 'absolute': 0 }
        }
        """
        assert self.absolute_index == state_details['index']['absolute']
        self.index_relative = state_details['index']['relative']
        self.seen_state = True
        self.moving = state_details['moving']
        self.position = state_details['position']
        self.lamella = state_details['lamella']

    def _consume_shade_state(self, state_details):
        """
        We consume the shade state to get the current position
        of the shade during movement.
        Example of shade_details
        {
            "target": { "blind": 74, "lamella": 100 },
            "current": { "blind": 18, "lamella": 100 },
            "disabled": false,
            "index": { "relative": 1, "absolute": 1 }
        }
        """
        assert self.absolute_index == state_details['index']['absolute']
        self.position = state_details['current']['blind']
        self.lamella = state_details['current']['lamella']

    async def operate_shade(self, blind=None, lamella=None) -> None:
        """
        Operate the lamella and blind.

        blind: 0 fully closed, 100 fully open
        lamella: 0 lamellas closed, 100 lamellas open
        """

        # With newer versions of dingz, we can just leave
        # either lamella or blind None (i.e. do not chang)
        # but currently we need to lookup the current state
        # of the shade first.
        if blind is None or lamella is None:
            # todo check v1.2
            await self.dingz.get_state()

            if blind is None:
                blind = self.current_blind_level()

            if lamella is None:
                if self.is_shade_opened():
                    # If the shade is currently completely opened (i.e. up), the lamella
                    # value is not really relevant (has no effect). We assume the
                    # lamella value to be 0, ie. closed.
                    # i.e. we set lamella to 45, raise blind to the top, and then back down again
                    # => de we expect the lamella to be set to 45 again, or does it get resetted to 0?
                    lamella = 0
                else:
                    lamella = self.current_lamella_level()

        url = URL(self.dingz.uri).join(URL("%s/%s" % (SHADE, self.absolute_index)))
        params = {"blind": str(blind), "lamella": str(lamella)}
        await make_call(self.dingz, uri=url, method="POST", parameters=params)

    async def shade_up(self) -> None:
        """Move the shade up."""
        await self.shade_command("up")

    async def shade_down(self) -> None:
        """Move the shade down."""
        await self.shade_command("down")

    async def shade_stop(self) -> None:
        """Stop the shade."""
        await self.shade_command("stop")

    async def lamella_open(self) -> None:
        """Open the lamella."""
        await self.operate_shade(lamella=100)

    async def lamella_close(self) -> None:
        """Close the lamella."""
        await self.operate_shade(lamella=0)

    async def lamella_stop(self) -> None:
        """Stop the lamella."""
        await self.shade_stop()

    async def shade_command(self, verb):
        """Create a command for the shade."""
        url = URL(self.dingz.uri).join(URL("%s/%s/%s" % (SHADE, self.absolute_index, verb)))
        await make_call(self.dingz, uri=url, method="POST")

    def current_blind_level(self):
        """Get the current blind level."""
        return self.position

    def current_lamella_level(self):
        """Get the current lamella level."""
        return self.lamella

    def is_shade_closed(self):
        """Get the closed state of a shade."""
        # When closed, we care if the lamellas are opened or not
        return (
                self.current_blind_level() == 0
                and self.current_lamella_level() == 0
        )

    def is_shade_opened(self):
        """Get the open state of a shade."""
        return self.current_blind_level() == 100

    def is_lamella_closed(self):
        """Get the closed state of a lamella."""
        return self.current_lamella_level() == 0

    def is_lamella_opened(self):
        """Get the open state of  lamella."""
        return self.current_lamella_level() == 100

    def is_shade_opening(self):
        """Get whether the shade if opening."""
        return self.moving == "up"

    def is_shade_closing(self):
        """Get whether the shade if closing."""
        return self.moving == "down"

    def is_moving(self):
        """Get whether the shade is moving"""
        return self.is_shade_opening() or self.is_shade_closing()

    def shade_name(self, shade_no):
        """Get the name of the shade."""
        return self.name


class ShadeRegistry(BaseRegistry[Shade]):
    def __init__(self, dingz):
        super().__init__(factory=lambda absolute_index: Shade(absolute_index, dingz))

    def _consume_config(self, blind_configs):
        for absolute_index, shade_config in enumerate(blind_configs):
            shade = self._get_or_create(absolute_index)
            shade._consume_config(shade_config)

    def _consume_device_state(self, device_states):
        for absolute_index, state in organize_by_absolute_index(device_states):
            shade = self._get_or_create(absolute_index)
            shade._consume_device_state(state)

    def _consume_shade_state(self, shade_states):
        for absolute_index, shade_state in organize_by_absolute_index(shade_states):
            shade = self._get_or_create(absolute_index)
            shade._consume_shade_state(shade_state)

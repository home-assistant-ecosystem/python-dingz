"""Base details for the dingz Python bindings."""

from __future__ import annotations

import asyncio
import socket
import sys
from typing import TYPE_CHECKING, Any

import aiohttp

if sys.version_info >= (3, 11):
    import asyncio as async_timeout
else:
    import async_timeout

from .constants import (
    CONTENT_TYPE,
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_TEXT_PLAIN,
    TIMEOUT,
    USER_AGENT,
)
from .exceptions import DingzConnectionError

if TYPE_CHECKING:
    from collections.abc import Mapping


async def make_call(
    self,
    uri: str,
    method: str = "GET",
    data: Any | None = None,
    json_data: dict | None = None,
    parameters: Mapping[str, str] | None = None,
    token: str | None = None,
) -> Any:
    """Handle the requests to the dingz unit."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": f"{CONTENT_TYPE_JSON}, {CONTENT_TYPE_TEXT_PLAIN}, */*",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if self._session is None:
        self._session = aiohttp.ClientSession()
        self._close_session = True

    try:
        async with async_timeout.timeout(TIMEOUT):
            response = await self._session.request(
                method,
                uri,
                data=data,
                json=json_data,
                params=parameters,
                headers=headers,
            )
    except asyncio.TimeoutError as exception:
        msg = "Timeout occurred while connecting to dingz unit"
        raise DingzConnectionError(msg) from exception
    except (aiohttp.ClientError, socket.gaierror) as exception:
        msg = "Error occurred while communicating with dingz"
        raise DingzConnectionError(msg) from exception

    if CONTENT_TYPE_JSON in response.headers.get(CONTENT_TYPE, ""):
        return await response.json()

    return response.text

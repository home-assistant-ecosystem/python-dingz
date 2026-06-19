from collections.abc import AsyncIterator
from typing import Any, Literal
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from yarl import URL

from dingz.rest import RestClient

from .snapshot import Snapshot, load_snapshots

_SNAPSHOTS = load_snapshots()


@pytest.fixture(
    params=_SNAPSHOTS,
    ids=lambda snapshot: snapshot.device_hash,
)
def snapshot(request: pytest.FixtureRequest) -> Snapshot:
    return request.param


@pytest_asyncio.fixture
async def rest_client_with_snapshot(snapshot: Snapshot) -> AsyncIterator[RestClient]:
    def side_effect(
        _method: Literal["GET"],
        endpoint: URL,
        *,
        ignore_content_type: bool = False,
    ) -> Any:
        endpoint_data = snapshot.endpoint_by_path(endpoint.path)
        if endpoint_data.error is not None:
            msg = "Error mocking is not yet implemented in test framework!"
            raise NotImplementedError(msg)
        return endpoint_data.value

    async with RestClient("127.0.0.1") as client:
        request_mock = AsyncMock(client._request, side_effect=side_effect)
        client._request = request_mock
        yield client

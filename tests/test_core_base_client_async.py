import pytest
from gravity_tse.core.base_client import BaseAsyncClient


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload

    def raise_for_status(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummySession:
    def __init__(self, payload):
        self._payload = payload
        self.closed = False

    def request(self, *args, **kwargs):
        return DummyResponse(self._payload)

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_base_async_make_request_success():
    client = BaseAsyncClient()
    client.session = DummySession({'ok': True})
    res = await client._make_async_request('http://example.com')
    assert res == {'ok': True}

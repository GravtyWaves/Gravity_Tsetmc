"""Base sync & async client classes for TSE API access"""
from typing import Any, Optional, Dict
import requests
import aiohttp
from .config import config
from .exceptions import TSEConnectionError


class BaseSyncClient:
    """Synchronous client helper using requests.Session."""

    def __init__(self, cfg: Optional[config.__class__] = None):
        self.cfg = cfg or config
        # Use a single requests Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update(self.cfg.HEADERS)

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        try:
            resp = self.session.request(method=method, url=url, timeout=self.cfg.REQUEST_TIMEOUT, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            raise TSEConnectionError(str(e))


class BaseAsyncClient:
    """Asynchronous client helper using aiohttp.ClientSession."""

    def __init__(self, cfg: Optional[config.__class__] = None):
        self.cfg = cfg or config
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.cfg.HEADERS)

    async def _make_async_request(self, url: str, method: str = 'GET', **kwargs) -> Any:
        await self._ensure_session()
        try:
            async with self.session.request(method=method, url=url, timeout=aiohttp.ClientTimeout(total=self.cfg.REQUEST_TIMEOUT), **kwargs) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as e:
            raise TSEConnectionError(str(e))

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

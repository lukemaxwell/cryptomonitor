"""
Defines a per-domain rate limiter to be used with aiohttp client session.

Adapted from:
https://stackoverflow.com/questions/49708101/aiohttp-rate-limiting-requests-per-second-by-domain
"""
import asyncio
import logging
from collections import defaultdict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RateLimiter:
    # domain -> lock:
    _locks = defaultdict(lambda: asyncio.Lock())

    # domain -> last request time
    _times = defaultdict(lambda: 0)

    request_delay = 5

    def __init__(self, url):
        self._host = urlparse(url).hostname

    async def __aenter__(self):
        # await self._lock
        async with self._lock:

            to_wait = self._to_wait_before_request()
            logger.info(
                f"Wait {round(to_wait, 2)} sec before next request to {self._host}"
            )
            await asyncio.sleep(to_wait)

    async def __aexit__(self, *args):
        logger.info(f"Request to {self._host} just finished")

        self._update_request_time()

    @property
    def _lock(self):
        """Lock that prevents multiple requests to same host."""
        return self._locks[self._host]

    def _to_wait_before_request(self):
        """What time we need to wait before request to host."""
        request_time = self._times[self._host]
        request_delay = self.request_delay
        now = asyncio.get_event_loop().time()
        to_wait = request_time + request_delay - now
        to_wait = max(0, to_wait)
        return to_wait

    def _update_request_time(self):
        now = asyncio.get_event_loop().time()
        self._times[self._host] = now

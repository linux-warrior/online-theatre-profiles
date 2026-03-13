from __future__ import annotations

import redis.asyncio as redis


class RedisCache:
    _client: redis.Redis

    def __init__(self, *, client: redis.Redis) -> None:
        self._client = client

    async def clear(self) -> None:
        await self._client.flushall()

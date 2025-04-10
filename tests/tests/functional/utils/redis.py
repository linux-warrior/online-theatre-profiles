from __future__ import annotations

import redis.asyncio as redis


class RedisCache:
    client: redis.Redis

    def __init__(self, *, client: redis.Redis) -> None:
        self.client = client

    async def clear(self) -> None:
        await self.client.flushall()

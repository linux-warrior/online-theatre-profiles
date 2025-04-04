from __future__ import annotations

from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends

from .cache import RedisCache
from ..base import AbstractCacheService
from .....db import RedisClientDep


class RedisCacheService(AbstractCacheService):
    redis_client: redis.Redis

    def __init__(self, *, redis_client: redis.Redis) -> None:
        self.redis_client = redis_client

    def get_cache(self,
                  *,
                  key_prefix: str | None = None,
                  key_version: str | None = None) -> RedisCache:
        return RedisCache(
            redis_client=self.redis_client,
            key_prefix=key_prefix,
            key_version=key_version,
        )


async def get_cache_service(redis_client: RedisClientDep) -> RedisCacheService:
    return RedisCacheService(redis_client=redis_client)


RedisCacheServiceDep = Annotated[RedisCacheService, Depends(get_cache_service)]

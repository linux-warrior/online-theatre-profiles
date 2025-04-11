from __future__ import annotations

from collections.abc import Callable, Awaitable, AsyncGenerator

import pytest_asyncio
import redis.asyncio as redis


from ..settings import settings
from ..utils.redis import RedisCache


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> AsyncGenerator[redis.Redis]:
    async with redis.Redis(host=settings.redis.host, port=settings.redis.port) as redis_client:
        yield redis_client


@pytest_asyncio.fixture
async def redis_cache(
        redis_client: redis.Redis,
) -> AsyncGenerator[RedisCache]:
    yield RedisCache(client=redis_client)


@pytest_asyncio.fixture(autouse=True)
async def clear_redis_cache(
        redis_client: redis.Redis,
) -> AsyncGenerator[Callable[[], Awaitable[None]]]:
    redis_cache = RedisCache(client=redis_client)

    async def _clear_redis_cache() -> None:
        await redis_cache.clear()

    await _clear_redis_cache()
    yield _clear_redis_cache
    await _clear_redis_cache()

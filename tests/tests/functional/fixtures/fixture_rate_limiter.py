from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
import redis.asyncio as redis

from ..settings import settings


@pytest_asyncio.fixture(scope='session')
async def _auth_redis_client() -> AsyncGenerator[redis.Redis]:
    async with (
        redis.Redis(
            host=settings.auth_redis.host,
            port=settings.auth_redis.port,
        ) as auth_redis_client,
    ):
        yield auth_redis_client


@pytest_asyncio.fixture(scope='function', autouse=True)
async def reset_rate_limit(_auth_redis_client: redis.Redis) -> None:
    await _auth_redis_client.flushdb()

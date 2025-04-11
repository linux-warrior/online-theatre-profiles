from __future__ import annotations

import pytest_asyncio
import redis.asyncio as redis


from ..settings import settings


@pytest_asyncio.fixture(scope='function', autouse=True)
async def reset_rate_limit():
    redis_client = redis.Redis(host=settings.auth_redis.host, port=settings.auth_redis.port, decode_responses=True)
    await redis_client.flushdb()

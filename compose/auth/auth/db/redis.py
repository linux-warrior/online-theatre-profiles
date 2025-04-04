from __future__ import annotations

from typing import Annotated

import redis.asyncio as redis
from fastapi import Request, Depends


async def get_redis_client(request: Request) -> redis.Redis:
    return request.state.redis_client


RedisClientDep = Annotated[redis.Redis, Depends(get_redis_client)]

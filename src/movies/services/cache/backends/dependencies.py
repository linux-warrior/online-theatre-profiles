from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import AbstractCacheService
from .redis import RedisCacheServiceDep


async def get_cache_service(cache_service: RedisCacheServiceDep) -> AbstractCacheService:
    return cache_service


CacheServiceDep = Annotated[AbstractCacheService, Depends(get_cache_service)]

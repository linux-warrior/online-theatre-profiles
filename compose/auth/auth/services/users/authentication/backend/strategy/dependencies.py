from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import Strategy
from .jwt import (
    AccessJWTStrategy,
    RefreshJWTStrategy,
)
from .....cache import CacheServiceDep
from ......core import settings


async def get_access_strategy(cache_service: CacheServiceDep) -> Strategy:
    return AccessJWTStrategy(
        secret=settings.auth.secret_key,
        lifetime_seconds=settings.auth.access_jwt_lifetime,
        cache_service=cache_service,
    )


async def get_refresh_strategy(cache_service: CacheServiceDep) -> Strategy:
    return RefreshJWTStrategy(
        secret=settings.auth.secret_key,
        lifetime_seconds=settings.auth.refresh_jwt_lifetime,
        token_audience=['users:refresh'],
        cache_service=cache_service,
    )


AccessStrategyDep = Annotated[Strategy, Depends(get_access_strategy)]
RefreshStrategyDep = Annotated[Strategy, Depends(get_refresh_strategy)]

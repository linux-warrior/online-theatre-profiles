from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import AbstractTokenStrategy
from .jwt import (
    AccessJWTStrategy,
    RefreshJWTStrategy,
)
from .....cache import CacheServiceDep
from .....jwt import JWTServiceDep
from ......core import settings


async def get_access_token_strategy(jwt_service: JWTServiceDep,
                                    cache_service: CacheServiceDep) -> AbstractTokenStrategy:
    return AccessJWTStrategy(
        lifetime=settings.auth.access_jwt_lifetime,
        jwt_service=jwt_service,
        cache_service=cache_service,
    )


async def get_refresh_token_strategy(jwt_service: JWTServiceDep,
                                     cache_service: CacheServiceDep) -> AbstractTokenStrategy:
    return RefreshJWTStrategy(
        lifetime=settings.auth.refresh_jwt_lifetime,
        audience=['users:refresh'],
        jwt_service=jwt_service,
        cache_service=cache_service,
    )


AccessTokenStrategyDep = Annotated[AbstractTokenStrategy, Depends(get_access_token_strategy)]
RefreshTokenStrategyDep = Annotated[AbstractTokenStrategy, Depends(get_refresh_token_strategy)]

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .backend import AuthenticationBackend
from .strategy import (
    JWTStrategy,
    AccessTokenProcessor,
    RefreshTokenProcessor,
)
from .transport import (
    BearerTransport,
)
from ....cache import CacheServiceDep
from ....jwt import JWTServiceDep
from .....core import settings


async def get_authentication_backend(cache_service: CacheServiceDep,
                                     jwt_service: JWTServiceDep) -> AuthenticationBackend:
    cache = cache_service.get_cache(key_prefix='jwt')
    access_token_strategy = JWTStrategy(
        token_processor=AccessTokenProcessor(
            cache=cache,
            lifetime=settings.auth.access_jwt_lifetime,
        ),
        lifetime=settings.auth.access_jwt_lifetime,
        jwt_service=jwt_service,
    )
    refresh_token_strategy = JWTStrategy(
        token_processor=RefreshTokenProcessor(
            cache=cache,
            lifetime=settings.auth.refresh_jwt_lifetime,
        ),
        lifetime=settings.auth.refresh_jwt_lifetime,
        audience=['users:refresh'],
        jwt_service=jwt_service,
    )

    return AuthenticationBackend(
        name='jwt',
        transport=BearerTransport(),
        access_token_strategy=access_token_strategy,
        refresh_token_strategy=refresh_token_strategy,
    )


AuthenticationBackendDep = Annotated[AuthenticationBackend, Depends(get_authentication_backend)]

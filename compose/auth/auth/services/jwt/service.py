from __future__ import annotations

import abc
from typing import Annotated

from fastapi import Depends

from .jwt import (
    AbstractJWTHelper,
    JWTHelper,
)


class AbstractJWTService(abc.ABC):
    @abc.abstractmethod
    def get_jwt_helper(self,
                       *,
                       secret_key: str | None = None,
                       algorithm: str | None = None) -> AbstractJWTHelper: ...


class JWTService(AbstractJWTService):
    def get_jwt_helper(self,
                       *,
                       secret_key: str | None = None,
                       algorithm: str | None = None) -> AbstractJWTHelper:
        return JWTHelper(secret_key=secret_key)


async def get_jwt_service() -> AbstractJWTService:
    return JWTService()


JWTServiceDep = Annotated[AbstractJWTService, Depends(get_jwt_service)]

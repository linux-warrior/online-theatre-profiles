from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status

from .backend import (
    AuthenticationBackend,
    AuthenticationBackendDep,
)
from ..manager import (
    UserManager,
    UserManagerDep,
)
from ....models.sqlalchemy import User


class Authenticator:
    backend: AuthenticationBackend
    user_manager: UserManager

    def __init__(self,
                 backend: AuthenticationBackend,
                 user_manager: UserManager) -> None:
        self.backend = backend
        self.user_manager = user_manager

    async def authenticate(self, *, token: str, is_superuser: bool = False) -> User:
        user = await self.backend.authenticate(token=token, user_manager=self.user_manager)

        if user and is_superuser and not user.is_superuser:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return user


async def get_authenticator(backend: AuthenticationBackendDep,
                            user_manager: UserManagerDep) -> Authenticator:
    return Authenticator(backend=backend, user_manager=user_manager)


AuthenticatorDep = Annotated[Authenticator, Depends(get_authenticator)]

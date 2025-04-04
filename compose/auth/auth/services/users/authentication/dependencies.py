from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .authenticator import AuthenticatorDep
from .backend import TokenDep
from ....models.sqlalchemy import User


async def get_current_user(token: TokenDep, authenticator: AuthenticatorDep) -> User:
    return await authenticator.authenticate(token=token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_superuser(token: TokenDep, authenticator: AuthenticatorDep) -> User:
    return await authenticator.authenticate(token=token, is_superuser=True)


CurrentSuperuserDep = Annotated[User, Depends(get_current_superuser)]

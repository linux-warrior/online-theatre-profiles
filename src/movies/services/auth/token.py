from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ...core import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.auth.oauth2_token_url,
    auto_error=False,
)
OAuth2TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_token(token: OAuth2TokenDep) -> str:
    return token


TokenDep = Annotated[str, Depends(get_token)]

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ...http import HttpClient
from ....core import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.auth.oauth2_token_url,
    auto_error=False,
)
OAuth2TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_token(token: OAuth2TokenDep) -> str:
    return token


TokenDep = Annotated[str, Depends(get_token)]


class TokenHttpClient(HttpClient):
    token: str

    def __init__(self, *, token: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.token = token

    def get_default_headers(self) -> dict:
        return {
            **super().get_default_headers(),
            'Authorization': f'Bearer {self.token}',
        }

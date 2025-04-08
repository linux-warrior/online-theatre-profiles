from __future__ import annotations

from typing import Annotated

import httpx
from fastapi.params import Depends

from .token import TokenDep
from ...core import settings
from ...dependencies import HTTPXClientDep


class AuthClient:
    httpx_client: httpx.AsyncClient
    token: str

    def __init__(self, *, httpx_client: httpx.AsyncClient, token: str) -> None:
        self.httpx_client = httpx_client
        self.token = token

    async def get_user_profile(self) -> dict:
        response = await self.httpx_client.get(
            url=settings.auth.user_profile_url,
            headers=self.get_headers(),
        )
        response.raise_for_status()
        return response.json()

    def get_headers(self) -> dict:
        return {
            'X-Request-Id': 'movies',
            'Authorization': f'Bearer {self.token}',
        }


def get_auth_client(httpx_client: HTTPXClientDep, token: TokenDep) -> AuthClient:
    return AuthClient(httpx_client=httpx_client, token=token)


AuthClientDep = Annotated[AuthClient, Depends(get_auth_client)]

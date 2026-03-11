from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends

from .token import TokenDep
from ....core import settings
from ....dependencies import HTTPXClientDep


class CurrentUserClient:
    _httpx_client: httpx.AsyncClient
    _token: str

    def __init__(self, *, httpx_client: httpx.AsyncClient, token: str) -> None:
        self._httpx_client = httpx_client
        self._token = token

    async def get_user_profile(self) -> dict:
        response = await self._httpx_client.get(
            url=settings.auth.user_profile_url,
            headers=self.get_headers(),
        )
        response.raise_for_status()
        return response.json()

    def get_headers(self) -> dict:
        return {
            'X-Request-Id': 'profiles',
            'Authorization': f'Bearer {self._token}',
        }


async def get_current_user_client(httpx_client: HTTPXClientDep, token: TokenDep) -> CurrentUserClient:
    return CurrentUserClient(httpx_client=httpx_client, token=token)


CurrentUserClientDep = Annotated[CurrentUserClient, Depends(get_current_user_client)]

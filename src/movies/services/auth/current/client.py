from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends

from .models import CurrentUser
from .token import (
    TokenDep,
    TokenHttpClient,
)
from ...http import HttpClient
from ....core import settings
from ....dependencies import HTTPXClientDep


class CurrentUserClient:
    http_client: HttpClient

    def __init__(self, *, httpx_client: httpx.AsyncClient, token: str) -> None:
        self.http_client = TokenHttpClient(
            httpx_client=httpx_client,
            base_url=settings.auth.api_v1_url,
            token=token,
        )

    async def get_user_profile(self) -> CurrentUser:
        response = await self.http_client.get(
            url=settings.auth.get_user_profile_url(),
        )

        return CurrentUser.model_validate(response.json())


async def get_current_user_client(httpx_client: HTTPXClientDep, token: TokenDep) -> CurrentUserClient:
    return CurrentUserClient(httpx_client=httpx_client, token=token)


CurrentUserClientDep = Annotated[CurrentUserClient, Depends(get_current_user_client)]

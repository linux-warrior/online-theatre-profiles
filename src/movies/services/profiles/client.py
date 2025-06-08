from __future__ import annotations

import uuid
from typing import Annotated

import httpx
from fastapi import Depends

from .models import (
    FilmRating,
    FilmReviews,
)
from ..auth import (
    TokenDep,
    TokenHttpClient,
)
from ..http import HttpClient
from ...core import settings
from ...dependencies import HTTPXClientDep


class ProfilesServiceClient:
    http_client: HttpClient

    def __init__(self, *, httpx_client: httpx.AsyncClient, token: str) -> None:
        self.http_client = TokenHttpClient(
            httpx_client=httpx_client,
            base_url=settings.profiles.api_v1_url,
            token=token,
        )

    async def get_film_rating(self, *, film_id: uuid.UUID) -> FilmRating:
        response = await self.http_client.get(
            settings.profiles.get_film_rating_url(film_id=film_id),
        )

        return FilmRating.model_validate(response.json())

    async def get_film_reviews(self, *, film_id: uuid.UUID) -> FilmReviews:
        response = await self.http_client.get(
            settings.profiles.get_film_reviews_url(film_id=film_id),
        )

        return FilmReviews.model_validate(response.json())


async def get_profiles_service_client(httpx_client: HTTPXClientDep, token: TokenDep) -> ProfilesServiceClient:
    return ProfilesServiceClient(httpx_client=httpx_client, token=token)


ProfilesServiceClientDep = Annotated[ProfilesServiceClient, Depends(get_profiles_service_client)]

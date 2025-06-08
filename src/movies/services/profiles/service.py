from __future__ import annotations

import abc
import uuid
from typing import Annotated, Any

import httpx
from fastapi import HTTPException, Depends, status

from .client import (
    ProfilesServiceClient,
    ProfilesServiceClientDep,
)
from .models import (
    FilmRating,
    FilmReviews,
)


class AbstractProfilesService(abc.ABC):
    @abc.abstractmethod
    async def get_film_rating(self, *, film_id: uuid.UUID) -> FilmRating | None: ...

    @abc.abstractmethod
    async def get_film_reviews(self, *, film_id: uuid.UUID) -> FilmReviews | None: ...


class ProfilesService(AbstractProfilesService):
    profiles_service_client: ProfilesServiceClient

    def __init__(self, *, profiles_service_client: ProfilesServiceClient) -> None:
        self.profiles_service_client = profiles_service_client

    async def get_film_rating(self, *, film_id: uuid.UUID) -> FilmRating | None:
        return await GetFilmRatingRequest(
            profiles_service_client=self.profiles_service_client,
            film_id=film_id,
        ).send_request()

    async def get_film_reviews(self, *, film_id: uuid.UUID) -> FilmReviews | None:
        return await GetFilmReviewsRequest(
            profiles_service_client=self.profiles_service_client,
            film_id=film_id,
        ).send_request()


class ProfilesServiceRequest[TResponse](abc.ABC):
    profiles_service_client: ProfilesServiceClient

    def __init__(self, *, profiles_service_client: ProfilesServiceClient) -> None:
        self.profiles_service_client = profiles_service_client

    async def send_request(self) -> TResponse | None:
        try:
            return await self._send_request()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == status.HTTP_403_FORBIDDEN:
                return None

            raise

        except httpx.HTTPError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    @abc.abstractmethod
    async def _send_request(self) -> TResponse:
        ...


class GetFilmRatingRequest(ProfilesServiceRequest[FilmRating]):
    film_id: uuid.UUID

    def __init__(self, *, film_id: uuid.UUID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.film_id = film_id

    async def _send_request(self) -> FilmRating:
        return await self.profiles_service_client.get_film_rating(film_id=self.film_id)


class GetFilmReviewsRequest(ProfilesServiceRequest[FilmReviews]):
    film_id: uuid.UUID

    def __init__(self, *, film_id: uuid.UUID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.film_id = film_id

    async def _send_request(self) -> FilmReviews:
        return await self.profiles_service_client.get_film_reviews(film_id=self.film_id)


async def get_profiles_service(profiles_service_client: ProfilesServiceClientDep) -> AbstractProfilesService:
    return ProfilesService(profiles_service_client=profiles_service_client)


ProfilesServiceDep = Annotated[AbstractProfilesService, Depends(get_profiles_service)]

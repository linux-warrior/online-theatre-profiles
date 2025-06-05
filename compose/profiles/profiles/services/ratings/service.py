from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    RatingNotFound,
    RatingCreateError,
    RatingUpdateError
)
from .models import (
    ReadRatingResponse,
    RatingCreate,
    RatingUpdate,
    DeleteRatingResponse,
)
from .repository import (
    RatingRepository,
    RatingRepositoryDep,
)
from ..auth import (
    AbstractPermissionService,
    PermissionServiceDep,
    AbstractPermissionChecker,
)
from ...models.schemas import (
    RatingSchema,
)
from ...models.sqlalchemy import (
    Rating,
)


class AbstractRatingService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, *, user_id: uuid.UUID) -> list[ReadRatingResponse]: ...

    @abc.abstractmethod
    async def get(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> ReadRatingResponse: ...

    @abc.abstractmethod
    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     rating_create: RatingCreate) -> ReadRatingResponse: ...

    @abc.abstractmethod
    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     rating_update: RatingUpdate) -> ReadRatingResponse: ...

    @abc.abstractmethod
    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteRatingResponse: ...


class RatingService(AbstractRatingService):
    repository: RatingRepository
    permission_checker: AbstractPermissionChecker

    def __init__(self,
                 *,
                 repository: RatingRepository,
                 permission_service: AbstractPermissionService) -> None:
        self.repository = repository
        self.permission_checker = permission_service.get_permission_checker()

    async def get_list(self, *, user_id: uuid.UUID) -> list[ReadRatingResponse]:
        await self.permission_checker.check_read_permission(user_id=user_id)

        ratings_list = await self.repository.get_list(user_id=user_id)

        return [self._get_read_rating_response(rating=rating) for rating in ratings_list]

    async def get(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> ReadRatingResponse:
        await self.permission_checker.check_read_permission(user_id=user_id)

        rating = await self.repository.get(user_id=user_id, film_id=film_id)

        if rating is None:
            raise RatingNotFound

        return self._get_read_rating_response(rating=rating)

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     rating_create: RatingCreate) -> ReadRatingResponse:
        await self.permission_checker.check_create_permission(user_id=user_id)

        try:
            rating = await self.repository.create(
                user_id=user_id,
                film_id=film_id,
                rating_create=rating_create,
            )

        except IntegrityError as e:
            raise RatingCreateError from e

        return self._get_read_rating_response(rating=rating)

    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     rating_update: RatingUpdate) -> ReadRatingResponse:
        await self.permission_checker.check_update_permission(user_id=user_id)

        try:
            update_rating_result = await self.repository.update(
                user_id=user_id,
                film_id=film_id,
                rating_update=rating_update,
            )

        except IntegrityError as e:
            raise RatingUpdateError from e

        if update_rating_result is None:
            raise RatingNotFound

        return await self.get(
            user_id=update_rating_result.user_id,
            film_id=update_rating_result.film_id,
        )

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteRatingResponse:
        await self.permission_checker.check_delete_permission(user_id=user_id)

        delete_rating_result = await self.repository.delete(user_id=user_id, film_id=film_id)

        if delete_rating_result is None:
            raise RatingNotFound

        return DeleteRatingResponse(
            id=delete_rating_result.id,
            user_id=delete_rating_result.user_id,
            film_id=delete_rating_result.film_id,
        )

    def _get_read_rating_response(self, *, rating: Rating) -> ReadRatingResponse:
        rating_schema = RatingSchema.model_validate(rating, from_attributes=True)
        read_rating_response_dict = rating_schema.model_dump()

        return ReadRatingResponse.model_validate(read_rating_response_dict)


async def get_ratings_service(repository: RatingRepositoryDep,
                              permission_service: PermissionServiceDep) -> AbstractRatingService:
    return RatingService(repository=repository, permission_service=permission_service)


RatingServiceDep = Annotated[AbstractRatingService, Depends(get_ratings_service)]

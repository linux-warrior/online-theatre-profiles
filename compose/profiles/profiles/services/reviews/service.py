from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    ReviewNotFound,
    ReviewCreateError,
    ReviewUpdateError,
)
from .models import (
    ReadReviewResponse,
    ReviewCreate,
    ReviewUpdate,
    DeleteReviewResponse,
    FilmReviewsResponse,
)
from .repository import (
    ReviewRepository,
    ReviewRepositoryDep,
)
from ..auth import (
    AbstractPermissionService,
    PermissionServiceDep,
    AbstractPermissionChecker,
)
from ..pagination import (
    PageParams,
)
from ...models.schemas import (
    ReviewSchema,
)
from ...models.sqlalchemy import (
    Review,
)


class AbstractReviewService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self,
                       *,
                       user_id: uuid.UUID,
                       page_params: PageParams) -> list[ReadReviewResponse]: ...

    @abc.abstractmethod
    async def get(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> ReadReviewResponse: ...

    @abc.abstractmethod
    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     review_create: ReviewCreate) -> ReadReviewResponse: ...

    @abc.abstractmethod
    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     review_update: ReviewUpdate) -> ReadReviewResponse: ...

    @abc.abstractmethod
    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteReviewResponse: ...

    @abc.abstractmethod
    async def get_film_reviews(self,
                               *,
                               film_id: uuid.UUID,
                               page_params: PageParams) -> FilmReviewsResponse: ...


class ReviewService(AbstractReviewService):
    _repository: ReviewRepository
    _permission_checker: AbstractPermissionChecker

    def __init__(self,
                 *,
                 repository: ReviewRepository,
                 permission_service: AbstractPermissionService) -> None:
        self._repository = repository
        self._permission_checker = permission_service.get_permission_checker()

    async def get_list(self,
                       *,
                       user_id: uuid.UUID,
                       page_params: PageParams) -> list[ReadReviewResponse]:
        await self._permission_checker.check_read_permission(user_id=user_id)

        reviews_list = await self._repository.get_list(
            user_id=user_id,
            page_params=page_params,
        )

        return [self._get_read_review_response(review=review) for review in reviews_list]

    async def get(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> ReadReviewResponse:
        await self._permission_checker.check_read_permission(user_id=user_id)

        review = await self._repository.get(user_id=user_id, film_id=film_id)

        if review is None:
            raise ReviewNotFound

        return self._get_read_review_response(review=review)

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     review_create: ReviewCreate) -> ReadReviewResponse:
        await self._permission_checker.check_create_permission(user_id=user_id)

        try:
            review = await self._repository.create(
                user_id=user_id,
                film_id=film_id,
                review_create=review_create,
            )

        except IntegrityError as e:
            raise ReviewCreateError from e

        return self._get_read_review_response(review=review)

    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     review_update: ReviewUpdate) -> ReadReviewResponse:
        await self._permission_checker.check_update_permission(user_id=user_id)

        try:
            update_review_result = await self._repository.update(
                user_id=user_id,
                film_id=film_id,
                review_update=review_update,
            )

        except IntegrityError as e:
            raise ReviewUpdateError from e

        if update_review_result is None:
            raise ReviewNotFound

        return await self.get(
            user_id=update_review_result.user_id,
            film_id=update_review_result.film_id,
        )

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteReviewResponse:
        await self._permission_checker.check_delete_permission(user_id=user_id)

        delete_review_result = await self._repository.delete(user_id=user_id, film_id=film_id)

        if delete_review_result is None:
            raise ReviewNotFound

        return DeleteReviewResponse(
            id=delete_review_result.id,
            user_id=delete_review_result.user_id,
            film_id=delete_review_result.film_id,
        )

    async def get_film_reviews(self,
                               *,
                               film_id: uuid.UUID,
                               page_params: PageParams) -> FilmReviewsResponse:
        await self._permission_checker.check_read_permission()

        reviews_list = await self._repository.get_film_reviews(
            film_id=film_id,
            page_params=page_params,
        )
        film_rating_result = await self._repository.get_film_rating(film_id=film_id)

        return FilmReviewsResponse(
            reviews=[self._get_read_review_response(review=review) for review in reviews_list],
            rating=film_rating_result.rating,
        )

    def _get_read_review_response(self, *, review: Review) -> ReadReviewResponse:
        review_schema = ReviewSchema.model_validate(review, from_attributes=True)
        read_review_response_dict = review_schema.model_dump()

        return ReadReviewResponse.model_validate(read_review_response_dict)


async def get_review_service(repository: ReviewRepositoryDep,
                             permission_service: PermissionServiceDep) -> AbstractReviewService:
    return ReviewService(repository=repository, permission_service=permission_service)


ReviewServiceDep = Annotated[AbstractReviewService, Depends(get_review_service)]

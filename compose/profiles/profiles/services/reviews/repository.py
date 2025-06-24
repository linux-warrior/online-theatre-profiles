from __future__ import annotations

import dataclasses
import decimal
import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
    update,
    delete,
    func,
)

from .models import (
    ReviewCreate,
    ReviewUpdate,
)
from ..pagination import (
    AbstractPaginationService,
    PaginationServiceDep,
    AbstractPaginator,
    PageParams,
)
from ...db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ...models.sqlalchemy import (
    Review,
    Profile,
)


@dataclasses.dataclass(kw_only=True)
class UpdateReviewResult:
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID


@dataclasses.dataclass(kw_only=True)
class DeleteReviewResult:
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID


@dataclasses.dataclass(kw_only=True)
class FilmRatingResult:
    rating: decimal.Decimal | None

    def __post_init__(self) -> None:
        if self.rating is not None:
            self.rating = self.rating.quantize(decimal.Decimal('0.1'), rounding=decimal.ROUND_DOWN)


class ReviewRepository:
    session: AsyncSession
    pagination_service: AbstractPaginationService

    def __init__(self,
                 *,
                 session: AsyncSession,
                 pagination_service: AbstractPaginationService) -> None:
        self.session = session
        self.pagination_service = pagination_service

    async def get_list(self,
                       *,
                       user_id: uuid.UUID,
                       page_params: PageParams) -> Sequence[Review]:
        statement = select(Review).join(
            Review.profile,
        ).where(
            Profile.user_id == user_id,
        )

        paginator: AbstractPaginator[tuple[Review]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=Review.id,
            timestamp_column=Review.modified,
        )
        page_statement = paginator.get_page(page_params=page_params)

        result = await self.session.execute(page_statement)

        return result.scalars().all()

    async def get(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> Review | None:
        statement = select(Review).join(
            Review.profile,
        ).where(
            Profile.user_id == user_id,
            Review.film_id == film_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     review_create: ReviewCreate) -> Review:
        review_create_dict = {
            **review_create.model_dump(),
            'profile_id': select(Profile.id).where(Profile.user_id == user_id),
            'film_id': film_id,
        }
        statement = insert(Review).values(review_create_dict).returning(Review)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     review_update: ReviewUpdate) -> UpdateReviewResult | None:
        review_update_dict = review_update.model_dump(exclude_unset=True)
        statement = update(Review).where(
            Profile.id == Review.profile_id,
            Profile.user_id == user_id,
            Review.film_id == film_id,
        ).values(review_update_dict).returning(
            Review.id,
            Profile.user_id,
            Review.film_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        update_review_row = result.one_or_none()

        if update_review_row is None:
            return None

        return UpdateReviewResult(
            id=update_review_row.id,
            user_id=update_review_row.user_id,
            film_id=update_review_row.film_id,
        )

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteReviewResult | None:
        statement = delete(Review).where(
            Profile.id == Review.profile_id,
            Profile.user_id == user_id,
            Review.film_id == film_id,
        ).returning(
            Review.id,
            Profile.user_id,
            Review.film_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_review_row = result.one_or_none()

        if delete_review_row is None:
            return None

        return DeleteReviewResult(
            id=delete_review_row.id,
            user_id=delete_review_row.user_id,
            film_id=delete_review_row.film_id,
        )

    async def get_film_reviews(self,
                               *,
                               film_id: uuid.UUID,
                               page_params: PageParams) -> Sequence[Review]:
        statement = select(Review).where(
            Review.film_id == film_id,
        )

        paginator: AbstractPaginator[tuple[Review]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=Review.id,
            timestamp_column=Review.modified,
        )
        page_statement = paginator.get_page(page_params=page_params)

        result = await self.session.execute(page_statement)

        return result.scalars().all()

    async def get_film_rating(self, *, film_id: uuid.UUID) -> FilmRatingResult:
        statement = select(
            func.avg(Review.rating).label('rating_avg'),
        ).where(
            Review.film_id == film_id,
        ).group_by(
            Review.film_id,
        )

        result = await self.session.execute(statement)

        rating_avg = result.scalar_one_or_none()

        return FilmRatingResult(rating=rating_avg)


async def get_review_repository(session: AsyncSessionDep,
                                pagination_service: PaginationServiceDep) -> ReviewRepository:
    return ReviewRepository(session=session, pagination_service=pagination_service)


ReviewRepositoryDep = Annotated[ReviewRepository, Depends(get_review_repository)]

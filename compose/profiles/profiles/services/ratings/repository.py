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
    RatingCreate,
    RatingUpdate,
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
    Rating,
    Profile,
)


@dataclasses.dataclass(kw_only=True)
class UpdateRatingResult:
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID


@dataclasses.dataclass(kw_only=True)
class DeleteRatingResult:
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID


@dataclasses.dataclass(kw_only=True)
class FilmRatingResult:
    rating: decimal.Decimal | None

    def __post_init__(self) -> None:
        if self.rating is not None:
            self.rating = self.rating.quantize(decimal.Decimal('0.1'), rounding=decimal.ROUND_DOWN)


class RatingRepository:
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
                       page_params: PageParams) -> Sequence[Rating]:
        statement = select(Rating).join(
            Rating.profile,
        ).where(
            Profile.user_id == user_id,
        )

        paginator: AbstractPaginator[tuple[Rating]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=Rating.id,
            timestamp_column=Rating.modified,
        )
        page_statement = paginator.get_page(page_params=page_params)

        result = await self.session.execute(page_statement)

        return result.scalars().all()

    async def get(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> Rating | None:
        statement = select(Rating).join(
            Rating.profile,
        ).where(
            Profile.user_id == user_id,
            Rating.film_id == film_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     rating_create: RatingCreate) -> Rating:
        rating_create_dict = {
            **rating_create.model_dump(),
            'profile_id': select(Profile.id).where(Profile.user_id == user_id),
            'film_id': film_id,
        }
        statement = insert(Rating).values([rating_create_dict]).returning(Rating)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     rating_update: RatingUpdate) -> UpdateRatingResult | None:
        rating_update_dict = rating_update.model_dump(exclude_unset=True)
        statement = update(Rating).where(
            Profile.id == Rating.profile_id,
            Profile.user_id == user_id,
            Rating.film_id == film_id,
        ).values(rating_update_dict).returning(Rating.id, Profile.user_id, Rating.film_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        update_rating_row = result.one_or_none()

        if update_rating_row is None:
            return None

        return UpdateRatingResult(
            id=update_rating_row.id,
            user_id=update_rating_row.user_id,
            film_id=update_rating_row.film_id,
        )

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteRatingResult | None:
        statement = delete(Rating).where(
            Profile.id == Rating.profile_id,
            Profile.user_id == user_id,
            Rating.film_id == film_id,
        ).returning(Rating.id, Profile.user_id, Rating.film_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_rating_row = result.one_or_none()

        if delete_rating_row is None:
            return None

        return DeleteRatingResult(
            id=delete_rating_row.id,
            user_id=delete_rating_row.user_id,
            film_id=delete_rating_row.film_id,
        )

    async def get_film_rating(self, *, film_id: uuid.UUID) -> FilmRatingResult:
        statement = select(
            func.avg(Rating.rating).label('rating_avg'),
        ).where(
            Rating.film_id == film_id,
        ).group_by(
            Rating.film_id,
        )

        result = await self.session.execute(statement)

        rating_avg = result.scalar_one_or_none()

        return FilmRatingResult(rating=rating_avg)


async def get_rating_repository(session: AsyncSessionDep,
                                pagination_service: PaginationServiceDep) -> RatingRepository:
    return RatingRepository(session=session, pagination_service=pagination_service)


RatingRepositoryDep = Annotated[RatingRepository, Depends(get_rating_repository)]

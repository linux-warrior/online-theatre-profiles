from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
    update,
    delete,
    Row,
)

from .models import (
    RatingCreate,
    RatingUpdate,
)
from ...db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ...models.sqlalchemy import (
    Rating,
    Profile,
)


class RatingRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, *, user_id: uuid.UUID) -> Sequence[Row[tuple[Rating, uuid.UUID]]]:
        statement = select(Rating, Profile.user_id).join(
            Rating.profile,
        ).where(
            Profile.user_id == user_id,
        ).order_by(
            Rating.created,
            Rating.id,
        )

        result = await self.session.execute(statement)

        return result.all()

    async def get(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> Row[tuple[Rating, uuid.UUID]] | None:
        statement = select(Rating, Profile.user_id).join(
            Rating.profile,
        ).where(
            Profile.user_id == user_id,
            Rating.film_id == film_id,
        )

        result = await self.session.execute(statement)

        return result.one_or_none()

    async def create(self, *, user_id: uuid.UUID, film_id: uuid.UUID, rating_create: RatingCreate) -> Rating:
        rating_create_dict = {
            **rating_create.model_dump(),
            'profile_id': select(Profile.id).where(Profile.user_id == user_id),
            'film_id': film_id,
        }
        statement = insert(Rating).values([rating_create_dict]).returning(Rating)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def update(self, *, user_id: uuid.UUID, film_id: uuid.UUID, rating_update: RatingUpdate) -> int:
        rating_update_dict = rating_update.model_dump(exclude_unset=True)
        statement = update(Rating).where(
            Profile.user_id == user_id,
            Rating.film_id == film_id,
        ).values(rating_update_dict)

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> int:
        statement = delete(Rating).where(
            Profile.user_id == user_id,
            Rating.film_id == film_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)


async def get_rating_repository(session: AsyncSessionDep) -> RatingRepository:
    return RatingRepository(session=session)


RatingRepositoryDep = Annotated[RatingRepository, Depends(get_rating_repository)]

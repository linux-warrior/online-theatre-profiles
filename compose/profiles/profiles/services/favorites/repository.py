from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
    delete,
    Row,
)

from ...db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ...models.sqlalchemy import (
    Favorite,
    Profile,
)


class FavoriteRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, *, user_id: uuid.UUID) -> Sequence[Row[tuple[Favorite, uuid.UUID]]]:
        statement = select(Favorite, Profile.user_id).join(
            Favorite.profile,
        ).where(
            Profile.user_id == user_id,
        ).order_by(
            Favorite.created,
            Favorite.id,
        )

        result = await self.session.execute(statement)

        return result.all()

    async def create(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> Favorite:
        statement = insert(Favorite).values([{
            'profile_id': select(Profile.id).where(Profile.user_id == user_id),
            'film_id': film_id,
        }]).returning(Favorite)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> int:
        statement = delete(Favorite).where(
            Profile.user_id == user_id,
            Favorite.film_id == film_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)


async def get_favorite_repository(session: AsyncSessionDep) -> FavoriteRepository:
    return FavoriteRepository(session=session)


FavoriteRepositoryDep = Annotated[FavoriteRepository, Depends(get_favorite_repository)]

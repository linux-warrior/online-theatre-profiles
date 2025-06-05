from __future__ import annotations

import dataclasses
import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
    delete,
)

from ...db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ...models.sqlalchemy import (
    Favorite,
    Profile,
)


@dataclasses.dataclass(kw_only=True)
class DeleteFavoriteResult:
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID


class FavoriteRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, *, user_id: uuid.UUID) -> Sequence[Favorite]:
        statement = select(Favorite).join(
            Favorite.profile,
        ).where(
            Profile.user_id == user_id,
        ).order_by(
            Favorite.created.desc(),
            Favorite.id.desc(),
        )

        result = await self.session.execute(statement)

        return result.scalars().all()

    async def create(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> Favorite:
        favorite_create_dict = {
            'profile_id': select(Profile.id).where(Profile.user_id == user_id),
            'film_id': film_id,
        }
        statement = insert(Favorite).values([favorite_create_dict]).returning(Favorite)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteFavoriteResult | None:
        statement = delete(Favorite).where(
            Profile.user_id == user_id,
            Favorite.film_id == film_id,
        ).returning(Favorite.id, Profile.user_id, Favorite.film_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_favorite_row = result.one_or_none()

        if delete_favorite_row is None:
            return None

        return DeleteFavoriteResult(
            id=delete_favorite_row.id,
            user_id=delete_favorite_row.user_id,
            film_id=delete_favorite_row.film_id,
        )


async def get_favorite_repository(session: AsyncSessionDep) -> FavoriteRepository:
    return FavoriteRepository(session=session)


FavoriteRepositoryDep = Annotated[FavoriteRepository, Depends(get_favorite_repository)]

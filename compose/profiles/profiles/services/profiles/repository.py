from __future__ import annotations

import uuid
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import (
    select,
    update,
    delete,
)

from .models import (
    ProfileCreate,
    ProfileUpdate,
)
from ...db.sqlalchemy import (
    AsyncSessionDep,
    AsyncSession
)
from ...models.sqlalchemy import (
    Profile,
)


class ProfileRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get(self, *, user_id: uuid.UUID) -> Profile | None:
        statement = select(Profile).where(Profile.user_id == user_id)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self, *, user_id: uuid.UUID, profile_create: ProfileCreate) -> Profile:
        profile_create_dict = {
            **profile_create.model_dump(),
            'user_id': user_id,
        }
        profile = Profile(**profile_create_dict)
        self.session.add(profile)

        await self.session.commit()
        await self.session.refresh(profile)

        return profile

    async def update(self, *, user_id: uuid.UUID, profile_update: ProfileUpdate) -> int:
        profile_update_dict = profile_update.model_dump(exclude_unset=True)
        statement = update(Profile).where(Profile.user_id == user_id).values(profile_update_dict)

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)

    async def delete(self, *, user_id: uuid.UUID) -> int:
        statement = delete(Profile).where(Profile.user_id == user_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)


async def get_profile_repository(session: AsyncSessionDep) -> ProfileRepository:
    return ProfileRepository(session=session)


ProfileRepositoryDep = Annotated[ProfileRepository, Depends(get_profile_repository)]

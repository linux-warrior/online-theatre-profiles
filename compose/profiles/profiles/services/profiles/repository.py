from __future__ import annotations

import dataclasses
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
    update,
    delete,
)

from .models import (
    ProfileCreate,
    ProfileUpdate,
)
from ...db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ...models.sqlalchemy import (
    Profile,
)


@dataclasses.dataclass(kw_only=True)
class UpdateProfileResult:
    id: uuid.UUID
    user_id: uuid.UUID


@dataclasses.dataclass(kw_only=True)
class DeleteProfileResult:
    id: uuid.UUID
    user_id: uuid.UUID


class ProfileRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get(self, *, user_id: uuid.UUID) -> Profile | None:
        statement = select(Profile).where(Profile.user_id == user_id)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     profile_create: ProfileCreate) -> Profile:
        profile_create_dict = {
            **profile_create.model_dump(),
            'user_id': user_id,
        }
        statement = insert(Profile).values([profile_create_dict]).returning(Profile)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def update(self,
                     *,
                     user_id:
                     uuid.UUID,
                     profile_update: ProfileUpdate) -> UpdateProfileResult | None:
        profile_update_dict = profile_update.model_dump(exclude_unset=True)
        statement = update(Profile).where(
            Profile.user_id == user_id,
        ).values(profile_update_dict).returning(Profile.id, Profile.user_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        update_profile_row = result.one_or_none()

        if update_profile_row is None:
            return None

        return UpdateProfileResult(
            id=update_profile_row.id,
            user_id=update_profile_row.user_id,
        )

    async def delete(self, *, user_id: uuid.UUID) -> DeleteProfileResult | None:
        statement = delete(Profile).where(
            Profile.user_id == user_id,
        ).returning(Profile.id, Profile.user_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_profile_row = result.one_or_none()

        if delete_profile_row is None:
            return None

        return DeleteProfileResult(
            id=delete_profile_row.id,
            user_id=delete_profile_row.user_id,
        )


async def get_profile_repository(session: AsyncSessionDep) -> ProfileRepository:
    return ProfileRepository(session=session)


ProfileRepositoryDep = Annotated[ProfileRepository, Depends(get_profile_repository)]

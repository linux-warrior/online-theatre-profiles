from __future__ import annotations

import dataclasses
import uuid
from typing import Annotated, Any

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
from ..cryptography import (
    AbstractCryptographyService,
    CryptographyServiceDep,
    AbstractDictEncryptionTool,
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
    profile_encryption_tool: AbstractDictEncryptionTool

    def __init__(self,
                 *,
                 session: AsyncSession,
                 cryptography_service: AbstractCryptographyService) -> None:
        self.session = session
        self.profile_encryption_tool = cryptography_service.get_dict_encryption_tool(
            fields=['phone_number'],
            salt='profiles.models.sqlalchemy.Profile',
        )

    async def get(self, *, user_id: uuid.UUID) -> Profile | None:
        statement = select(Profile).where(Profile.user_id == user_id)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     profile_create: ProfileCreate) -> Profile:
        profile_create_dict: dict[str, Any] = {
            **profile_create.model_dump(),
            'user_id': user_id,
        }
        profile_create_dict = self.profile_encryption_tool.encrypt(profile_create_dict)

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
        profile_update_dict = self.profile_encryption_tool.encrypt(profile_update_dict)

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


async def get_profile_repository(session: AsyncSessionDep,
                                 cryptography_service: CryptographyServiceDep) -> ProfileRepository:
    return ProfileRepository(session=session, cryptography_service=cryptography_service)


ProfileRepositoryDep = Annotated[ProfileRepository, Depends(get_profile_repository)]

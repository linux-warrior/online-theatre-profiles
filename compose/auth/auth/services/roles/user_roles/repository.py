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

from ....db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ....models.sqlalchemy import (
    UserRole,
)


@dataclasses.dataclass(kw_only=True)
class DeleteUserRoleResult:
    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID


class UserRoleRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, *, user_id: uuid.UUID) -> Sequence[UserRole]:
        statement = select(UserRole).where(
            UserRole.user_id == user_id,
        ).order_by(
            UserRole.created,
            UserRole.id,
        )

        result = await self.session.execute(statement)

        return result.scalars().all()

    async def create(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
        user_role_create_dict = {
            'user_id': user_id,
            'role_id': role_id,
        }
        statement = insert(UserRole).values(user_role_create_dict).returning(UserRole)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def delete(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> DeleteUserRoleResult | None:
        statement = delete(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        ).returning(
            UserRole.id,
            UserRole.user_id,
            UserRole.role_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_user_role_row = result.one_or_none()

        if delete_user_role_row is None:
            return None

        return DeleteUserRoleResult(
            id=delete_user_role_row.id,
            user_id=delete_user_role_row.user_id,
            role_id=delete_user_role_row.role_id,
        )


async def get_user_role_repository(session: AsyncSessionDep) -> UserRoleRepository:
    return UserRoleRepository(session=session)


UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends(get_user_role_repository)]

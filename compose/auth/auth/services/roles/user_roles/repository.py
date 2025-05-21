from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import (
    select,
    delete,
)

from ....db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ....models.sqlalchemy import (
    UserRole,
)


class UserRoleRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, *, user_id: uuid.UUID) -> Sequence[UserRole]:
        statement = select(UserRole).where(
            UserRole.user_id == user_id,
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
        )
        self.session.add(user_role)

        await self.session.commit()
        await self.session.refresh(user_role)

        return user_role

    async def delete(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> int:
        statement = delete(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)


async def get_user_role_repository(session: AsyncSessionDep) -> UserRoleRepository:
    return UserRoleRepository(session=session)


UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends(get_user_role_repository)]

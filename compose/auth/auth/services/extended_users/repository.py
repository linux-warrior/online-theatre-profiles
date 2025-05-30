from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    select,
)

from ...db.sqlalchemy import (
    AsyncSessionDep,
    AsyncSession
)
from ...models.sqlalchemy import (
    Role,
    UserRole,
    Permission,
    RolePermission,
)


class ExtendedUserRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_user_permissions(self, *, user_id: uuid.UUID) -> Sequence[Permission]:
        statement = select(
            Permission,
        ).join(
            Permission.role_permissions,
        ).join(
            RolePermission.role,
        ).join(
            Role.user_roles,
        ).where(
            UserRole.user_id == user_id,
        ).order_by(
            Permission.created,
            Permission.id,
        ).distinct()

        result = await self.session.execute(statement)

        return result.scalars().all()


async def get_extended_user_repository(session: AsyncSessionDep) -> ExtendedUserRepository:
    return ExtendedUserRepository(session=session)


ExtendedUserRepositoryDep = Annotated[ExtendedUserRepository, Depends(get_extended_user_repository)]

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
    RolePermission,
)


class RolePermissionRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, *, role_id: uuid.UUID) -> Sequence[RolePermission]:
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> RolePermission:
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )
        self.session.add(role_permission)

        await self.session.commit()
        await self.session.refresh(role_permission)

        return role_permission

    async def delete(self, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> int:
        statement = delete(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)


async def get_role_permission_repository(session: AsyncSessionDep) -> RolePermissionRepository:
    return RolePermissionRepository(session=session)


RolePermissionRepositoryDep = Annotated[RolePermissionRepository, Depends(get_role_permission_repository)]

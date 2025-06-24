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
    RolePermission,
)


@dataclasses.dataclass(kw_only=True)
class DeleteRolePermissionResult:
    id: uuid.UUID
    role_id: uuid.UUID
    permission_id: uuid.UUID


class RolePermissionRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, *, role_id: uuid.UUID) -> Sequence[RolePermission]:
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
        ).order_by(
            RolePermission.created,
            RolePermission.id,
        )

        result = await self.session.execute(statement)

        return result.scalars().all()

    async def create(self, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> RolePermission:
        role_permission_create_dict = {
            'role_id': role_id,
            'permission_id': permission_id,
        }
        statement = insert(RolePermission).values(role_permission_create_dict).returning(RolePermission)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def delete(self,
                     *,
                     role_id: uuid.UUID,
                     permission_id: uuid.UUID) -> DeleteRolePermissionResult | None:
        statement = delete(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        ).returning(
            RolePermission.id,
            RolePermission.role_id,
            RolePermission.permission_id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_role_permission_row = result.one_or_none()

        if delete_role_permission_row is None:
            return None

        return DeleteRolePermissionResult(
            id=delete_role_permission_row.id,
            role_id=delete_role_permission_row.role_id,
            permission_id=delete_role_permission_row.permission_id,
        )


async def get_role_permission_repository(session: AsyncSessionDep) -> RolePermissionRepository:
    return RolePermissionRepository(session=session)


RolePermissionRepositoryDep = Annotated[RolePermissionRepository, Depends(get_role_permission_repository)]

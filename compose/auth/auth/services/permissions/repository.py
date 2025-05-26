from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import (
    select,
    update,
    delete,
)

from .models import (
    PermissionCreate,
    PermissionUpdate,
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


class PermissionRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self) -> Sequence[Permission]:
        statement = select(Permission).order_by(Permission.created, Permission.id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get(self, *, permission_id: uuid.UUID) -> Permission | None:
        statement = select(Permission).where(Permission.id == permission_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, *, permission_create: PermissionCreate) -> Permission:
        permission_create_dict = permission_create.model_dump()
        permission = Permission(**permission_create_dict)
        self.session.add(permission)

        await self.session.commit()
        await self.session.refresh(permission)

        return permission

    async def update(self, *, permission_id: uuid.UUID, permission_update: PermissionUpdate) -> int:
        permission_update_dict = permission_update.model_dump(exclude_unset=True)
        statement = update(Permission).where(Permission.id == permission_id).values(permission_update_dict)

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)

    async def delete(self, *, permission_id: uuid.UUID) -> int:
        statement = delete(Permission).where(Permission.id == permission_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)

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


async def get_permission_repository(session: AsyncSessionDep) -> PermissionRepository:
    return PermissionRepository(session=session)


PermissionRepositoryDep = Annotated[PermissionRepository, Depends(get_permission_repository)]

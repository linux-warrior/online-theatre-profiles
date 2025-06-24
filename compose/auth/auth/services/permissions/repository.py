from __future__ import annotations

import dataclasses
import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
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
    Permission,
)


@dataclasses.dataclass(kw_only=True)
class UpdatePermissionResult:
    id: uuid.UUID


@dataclasses.dataclass(kw_only=True)
class DeletePermissionResult:
    id: uuid.UUID


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
        statement = insert(Permission).values(permission_create_dict).returning(Permission)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def update(self,
                     *,
                     permission_id: uuid.UUID,
                     permission_update: PermissionUpdate) -> UpdatePermissionResult | None:
        permission_update_dict = permission_update.model_dump(exclude_unset=True)
        statement = update(Permission).where(
            Permission.id == permission_id,
        ).values(permission_update_dict).returning(
            Permission.id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        update_permission_row = result.one_or_none()

        if update_permission_row is None:
            return None

        return UpdatePermissionResult(
            id=update_permission_row.id,
        )

    async def delete(self, *, permission_id: uuid.UUID) -> DeletePermissionResult | None:
        statement = delete(Permission).where(
            Permission.id == permission_id,
        ).returning(
            Permission.id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_permission_row = result.one_or_none()

        if delete_permission_row is None:
            return None

        return DeletePermissionResult(
            id=delete_permission_row.id,
        )


async def get_permission_repository(session: AsyncSessionDep) -> PermissionRepository:
    return PermissionRepository(session=session)


PermissionRepositoryDep = Annotated[PermissionRepository, Depends(get_permission_repository)]

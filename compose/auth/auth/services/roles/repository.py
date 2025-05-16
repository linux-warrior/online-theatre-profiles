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
    RoleCreate,
    RoleUpdate,
)
from ...db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ...models.sqlalchemy import (
    Role,
)


class RoleRepository:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self) -> Sequence[Role]:
        statement = select(Role)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get(self, *, role_id: uuid.UUID) -> Role | None:
        statement = select(Role).where(Role.id == role_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, *, role_create: RoleCreate) -> Role:
        role_create_dict = role_create.model_dump()
        role = Role(**role_create_dict)
        self.session.add(role)

        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> int:
        role_update_dict = role_update.model_dump(exclude_unset=True)
        statement = update(Role).where(Role.id == role_id).values(role_update_dict)

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)

    async def delete(self, *, role_id: uuid.UUID) -> int:
        statement = delete(Role).where(Role.id == role_id)

        result = await self.session.execute(statement)
        await self.session.commit()

        return cast(int, result.rowcount)


async def get_role_repository(session: AsyncSessionDep) -> RoleRepository:
    return RoleRepository(session=session)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]

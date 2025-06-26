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
    RoleCreate,
    RoleUpdate,
)
from ..pagination import (
    AbstractPaginationService,
    PaginationServiceDep,
    AbstractPaginator,
    PageParams,
)
from ...db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ...models.sqlalchemy import (
    Role,
)


@dataclasses.dataclass(kw_only=True)
class UpdateRoleResult:
    id: uuid.UUID


@dataclasses.dataclass(kw_only=True)
class DeleteRoleResult:
    id: uuid.UUID


class RoleRepository:
    session: AsyncSession
    pagination_service: AbstractPaginationService

    def __init__(self,
                 *,
                 session: AsyncSession,
                 pagination_service: AbstractPaginationService) -> None:
        self.session = session
        self.pagination_service = pagination_service

    async def get_list(self, *, page_params: PageParams) -> Sequence[Role]:
        statement = select(Role)

        paginator: AbstractPaginator[tuple[Role]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=Role.id,
            timestamp_column=Role.modified,
        )
        page_statement = paginator.get_page(page_params=page_params)

        result = await self.session.execute(page_statement)

        return result.scalars().all()

    async def get(self, *, role_id: uuid.UUID) -> Role | None:
        statement = select(Role).where(Role.id == role_id)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self, *, role_create: RoleCreate) -> Role:
        role_create_dict = role_create.model_dump()
        statement = insert(Role).values(role_create_dict).returning(Role)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> UpdateRoleResult | None:
        role_update_dict = role_update.model_dump(exclude_unset=True)
        statement = update(Role).where(
            Role.id == role_id,
        ).values(role_update_dict).returning(
            Role.id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        update_role_row = result.one_or_none()

        if update_role_row is None:
            return None

        return UpdateRoleResult(
            id=update_role_row.id,
        )

    async def delete(self, *, role_id: uuid.UUID) -> DeleteRoleResult | None:
        statement = delete(Role).where(
            Role.id == role_id,
        ).returning(
            Role.id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        delete_role_row = result.one_or_none()

        if delete_role_row is None:
            return None

        return DeleteRoleResult(
            id=delete_role_row.id,
        )


async def get_role_repository(session: AsyncSessionDep,
                              pagination_service: PaginationServiceDep) -> RoleRepository:
    return RoleRepository(session=session, pagination_service=pagination_service)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]

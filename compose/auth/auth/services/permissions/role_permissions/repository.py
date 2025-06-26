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

from ...pagination import (
    AbstractPaginationService,
    PaginationServiceDep,
    AbstractPaginator,
    PageParams,
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
    pagination_service: AbstractPaginationService

    def __init__(self,
                 *,
                 session: AsyncSession,
                 pagination_service: AbstractPaginationService) -> None:
        self.session = session
        self.pagination_service = pagination_service

    async def get_list(self,
                       *,
                       role_id: uuid.UUID,
                       page_params: PageParams) -> Sequence[RolePermission]:
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
        )

        paginator: AbstractPaginator[tuple[RolePermission]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=RolePermission.id,
            timestamp_column=RolePermission.created,
        )
        page_statement = paginator.get_page(page_params=page_params)

        result = await self.session.execute(page_statement)

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


async def get_role_permission_repository(session: AsyncSessionDep,
                                         pagination_service: PaginationServiceDep) -> RolePermissionRepository:
    return RolePermissionRepository(session=session, pagination_service=pagination_service)


RolePermissionRepositoryDep = Annotated[RolePermissionRepository, Depends(get_role_permission_repository)]

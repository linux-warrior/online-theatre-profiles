from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    RolePermissionNotFound,
    RolePermissionCreateError,
)
from .models import (
    ReadRolePermissionResponse,
    DeleteRolePermissionResponse,
)
from .repository import (
    RolePermissionRepository,
    RolePermissionRepositoryDep,
)


class AbstractRolePermissionService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, *, role_id: uuid.UUID) -> list[ReadRolePermissionResponse]: ...

    @abc.abstractmethod
    async def create(self, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> ReadRolePermissionResponse: ...

    @abc.abstractmethod
    async def delete(self, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> DeleteRolePermissionResponse: ...


class RolePermissionService(AbstractRolePermissionService):
    repository: RolePermissionRepository

    def __init__(self, *, repository: RolePermissionRepository) -> None:
        self.repository = repository

    async def get_list(self, *, role_id: uuid.UUID) -> list[ReadRolePermissionResponse]:
        role_permissions_list = await self.repository.get_list(role_id=role_id)

        return [
            ReadRolePermissionResponse.model_validate(role_permission, from_attributes=True)
            for role_permission in role_permissions_list
        ]

    async def create(self, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> ReadRolePermissionResponse:
        try:
            role_permission = await self.repository.create(role_id=role_id, permission_id=permission_id)
        except IntegrityError as e:
            raise RolePermissionCreateError from e

        return ReadRolePermissionResponse.model_validate(role_permission, from_attributes=True)

    async def delete(self, *, role_id: uuid.UUID, permission_id: uuid.UUID) -> DeleteRolePermissionResponse:
        rows_count = await self.repository.delete(role_id=role_id, permission_id=permission_id)

        if not rows_count:
            raise RolePermissionNotFound

        return DeleteRolePermissionResponse(id=role_id)


async def get_role_permission_service(repository: RolePermissionRepositoryDep) -> AbstractRolePermissionService:
    return RolePermissionService(repository=repository)


RolePermissionServiceDep = Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)]

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
from ....models.schemas import (
    RolePermissionSchema,
)
from ....models.sqlalchemy import (
    RolePermission,
)


class AbstractRolePermissionService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, *, role_id: uuid.UUID) -> list[ReadRolePermissionResponse]: ...

    @abc.abstractmethod
    async def create(self,
                     *,
                     role_id: uuid.UUID,
                     permission_id: uuid.UUID) -> ReadRolePermissionResponse: ...

    @abc.abstractmethod
    async def delete(self,
                     *,
                     role_id: uuid.UUID,
                     permission_id: uuid.UUID) -> DeleteRolePermissionResponse: ...


class RolePermissionService(AbstractRolePermissionService):
    repository: RolePermissionRepository

    def __init__(self, *, repository: RolePermissionRepository) -> None:
        self.repository = repository

    async def get_list(self, *, role_id: uuid.UUID) -> list[ReadRolePermissionResponse]:
        role_permissions_list = await self.repository.get_list(role_id=role_id)

        return [
            self._get_read_role_permission_response(role_permission=role_permission)
            for role_permission in role_permissions_list
        ]

    async def create(self,
                     *,
                     role_id: uuid.UUID,
                     permission_id: uuid.UUID) -> ReadRolePermissionResponse:
        try:
            role_permission = await self.repository.create(
                role_id=role_id,
                permission_id=permission_id,
            )

        except IntegrityError as e:
            raise RolePermissionCreateError from e

        return self._get_read_role_permission_response(role_permission=role_permission)

    async def delete(self,
                     *,
                     role_id: uuid.UUID,
                     permission_id: uuid.UUID) -> DeleteRolePermissionResponse:
        delete_role_permission_result = await self.repository.delete(
            role_id=role_id,
            permission_id=permission_id,
        )

        if delete_role_permission_result is None:
            raise RolePermissionNotFound

        return DeleteRolePermissionResponse(
            id=delete_role_permission_result.id,
            role_id=delete_role_permission_result.role_id,
            permission_id=delete_role_permission_result.permission_id,
        )

    def _get_read_role_permission_response(self,
                                           *,
                                           role_permission: RolePermission) -> ReadRolePermissionResponse:
        role_permission_schema = RolePermissionSchema.model_validate(role_permission, from_attributes=True)
        read_role_permission_response_dict = role_permission_schema.model_dump()

        return ReadRolePermissionResponse.model_validate(read_role_permission_response_dict)


async def get_role_permission_service(repository: RolePermissionRepositoryDep) -> AbstractRolePermissionService:
    return RolePermissionService(repository=repository)


RolePermissionServiceDep = Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)]

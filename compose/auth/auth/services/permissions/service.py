from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    PermissionNotFound,
    PermissionCreateError,
    PermissionUpdateError,
)
from .models import (
    ReadPermissionResponse,
    PermissionCreate,
    PermissionUpdate,
    DeletePermissionResponse,
)
from .repository import (
    PermissionRepository,
    PermissionRepositoryDep,
)
from ..pagination import (
    PageParams,
)
from ...models.schemas import (
    PermissionSchema,
)
from ...models.sqlalchemy import (
    Permission,
)


class AbstractPermissionService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, *, page_params: PageParams) -> list[ReadPermissionResponse]: ...

    @abc.abstractmethod
    async def get(self, *, permission_id: uuid.UUID) -> ReadPermissionResponse: ...

    @abc.abstractmethod
    async def create(self, *, permission_create: PermissionCreate) -> ReadPermissionResponse: ...

    @abc.abstractmethod
    async def update(self,
                     *,
                     permission_id: uuid.UUID,
                     permission_update: PermissionUpdate) -> ReadPermissionResponse: ...

    @abc.abstractmethod
    async def delete(self, *, permission_id: uuid.UUID) -> DeletePermissionResponse: ...


class PermissionService(AbstractPermissionService):
    repository: PermissionRepository

    def __init__(self, *, repository: PermissionRepository) -> None:
        self.repository = repository

    async def get_list(self, *, page_params: PageParams) -> list[ReadPermissionResponse]:
        permissions_list = await self.repository.get_list(page_params=page_params)

        return [
            self._get_read_permission_response(permission=permission)
            for permission in permissions_list
        ]

    async def get(self, *, permission_id: uuid.UUID) -> ReadPermissionResponse:
        permission = await self.repository.get(permission_id=permission_id)

        if permission is None:
            raise PermissionNotFound

        return self._get_read_permission_response(permission=permission)

    async def create(self, *, permission_create: PermissionCreate) -> ReadPermissionResponse:
        try:
            permission = await self.repository.create(permission_create=permission_create)
        except IntegrityError as e:
            raise PermissionCreateError from e

        return self._get_read_permission_response(permission=permission)

    async def update(self,
                     *,
                     permission_id: uuid.UUID,
                     permission_update: PermissionUpdate) -> ReadPermissionResponse:
        try:
            update_permission_result = await self.repository.update(
                permission_id=permission_id,
                permission_update=permission_update,
            )

        except IntegrityError as e:
            raise PermissionUpdateError from e

        if update_permission_result is None:
            raise PermissionNotFound

        return await self.get(permission_id=permission_id)

    async def delete(self, *, permission_id: uuid.UUID) -> DeletePermissionResponse:
        delete_permission_result = await self.repository.delete(permission_id=permission_id)

        if delete_permission_result is None:
            raise PermissionNotFound

        return DeletePermissionResponse(id=permission_id)

    def _get_read_permission_response(self, *, permission: Permission) -> ReadPermissionResponse:
        permission_schema = PermissionSchema.model_validate(permission, from_attributes=True)
        read_permission_response_dict = permission_schema.model_dump()

        return ReadPermissionResponse.model_validate(read_permission_response_dict)


async def get_permission_service(repository: PermissionRepositoryDep) -> AbstractPermissionService:
    return PermissionService(repository=repository)


PermissionServiceDep = Annotated[AbstractPermissionService, Depends(get_permission_service)]

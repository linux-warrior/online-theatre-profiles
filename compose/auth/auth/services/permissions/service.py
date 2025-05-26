from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    PermissionNotFound,
    PermissionAlreadyExists,
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


class AbstractPermissionService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self) -> list[ReadPermissionResponse]: ...

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

    @abc.abstractmethod
    async def get_user_permissions(self, *, user_id: uuid.UUID) -> list[ReadPermissionResponse]: ...


class PermissionService(AbstractPermissionService):
    repository: PermissionRepository

    def __init__(self, *, repository: PermissionRepository) -> None:
        self.repository = repository

    async def get_list(self) -> list[ReadPermissionResponse]:
        permissions_list = await self.repository.get_list()

        return [
            ReadPermissionResponse.model_validate(permission, from_attributes=True)
            for permission in permissions_list
        ]

    async def get(self, *, permission_id: uuid.UUID) -> ReadPermissionResponse:
        permission = await self.repository.get(permission_id=permission_id)

        if permission is None:
            raise PermissionNotFound

        return ReadPermissionResponse.model_validate(permission, from_attributes=True)

    async def create(self, *, permission_create: PermissionCreate) -> ReadPermissionResponse:
        try:
            permission = await self.repository.create(permission_create=permission_create)
        except IntegrityError as e:
            raise PermissionAlreadyExists from e

        return ReadPermissionResponse.model_validate(permission, from_attributes=True)

    async def update(self,
                     *,
                     permission_id: uuid.UUID,
                     permission_update: PermissionUpdate) -> ReadPermissionResponse:
        try:
            rows_count = await self.repository.update(
                permission_id=permission_id,
                permission_update=permission_update,
            )
        except IntegrityError as e:
            raise PermissionAlreadyExists from e

        if not rows_count:
            raise PermissionNotFound

        return await self.get(permission_id=permission_id)

    async def delete(self, *, permission_id: uuid.UUID) -> DeletePermissionResponse:
        rows_count = await self.repository.delete(permission_id=permission_id)

        if not rows_count:
            raise PermissionNotFound

        return DeletePermissionResponse(id=permission_id)

    async def get_user_permissions(self, *, user_id: uuid.UUID) -> list[ReadPermissionResponse]:
        permissions_list = await self.repository.get_user_permissions(user_id=user_id)

        return [
            ReadPermissionResponse.model_validate(permission, from_attributes=True)
            for permission in permissions_list
        ]


async def get_permission_service(repository: PermissionRepositoryDep) -> AbstractPermissionService:
    return PermissionService(repository=repository)


PermissionServiceDep = Annotated[AbstractPermissionService, Depends(get_permission_service)]

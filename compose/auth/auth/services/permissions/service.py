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
    PermissionRead,
    PermissionCreate,
    PermissionUpdate,
    PermissionDelete,
)
from .repository import (
    PermissionRepository,
    PermissionRepositoryDep,
)


class AbstractPermissionService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self) -> list[PermissionRead]: ...

    @abc.abstractmethod
    async def get(self, *, permission_id: uuid.UUID) -> PermissionRead: ...

    @abc.abstractmethod
    async def create(self, *, permission_create: PermissionCreate) -> PermissionRead: ...

    @abc.abstractmethod
    async def update(self,
                     *,
                     permission_id: uuid.UUID,
                     permission_update: PermissionUpdate) -> PermissionRead: ...

    @abc.abstractmethod
    async def delete(self, *, permission_id: uuid.UUID) -> PermissionDelete: ...


class PermissionService(AbstractPermissionService):
    repository: PermissionRepository

    def __init__(self, *, repository: PermissionRepository) -> None:
        self.repository = repository

    async def get_list(self) -> list[PermissionRead]:
        permissions_list = await self.repository.get_list()

        return [
            PermissionRead.model_validate(permission, from_attributes=True)
            for permission in permissions_list
        ]

    async def get(self, *, permission_id: uuid.UUID) -> PermissionRead:
        permission = await self.repository.get(permission_id=permission_id)

        if permission is None:
            raise PermissionNotFound

        return PermissionRead.model_validate(permission, from_attributes=True)

    async def create(self, *, permission_create: PermissionCreate) -> PermissionRead:
        try:
            permission = await self.repository.create(permission_create=permission_create)
        except IntegrityError as e:
            raise PermissionAlreadyExists from e

        return PermissionRead.model_validate(permission, from_attributes=True)

    async def update(self,
                     *,
                     permission_id: uuid.UUID,
                     permission_update: PermissionUpdate) -> PermissionRead:
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

    async def delete(self, *, permission_id: uuid.UUID) -> PermissionDelete:
        rows_count = await self.repository.delete(permission_id=permission_id)

        if not rows_count:
            raise PermissionNotFound

        return PermissionDelete(id=permission_id)


async def get_permission_service(repository: PermissionRepositoryDep) -> AbstractPermissionService:
    return PermissionService(repository=repository)


PermissionServiceDep = Annotated[AbstractPermissionService, Depends(get_permission_service)]

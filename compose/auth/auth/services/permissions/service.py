from __future__ import annotations

import abc
import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from .models import (
    PermissionCreate,
    PermissionUpdate,
)
from .repository import (
    PermissionRepository,
    PermissionRepositoryDep,
)
from ...models.sqlalchemy import (
    Permission,
)


class AbstractPermissionService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self) -> Sequence[Permission]: ...

    @abc.abstractmethod
    async def get(self, *, permission_id: uuid.UUID) -> Permission | None: ...

    @abc.abstractmethod
    async def create(self, *, permission_create: PermissionCreate) -> Permission: ...

    @abc.abstractmethod
    async def update(self, *, permission_id: uuid.UUID, permission_update: PermissionUpdate) -> Permission | None: ...

    @abc.abstractmethod
    async def delete(self, *, permission_id: uuid.UUID) -> None: ...


class PermissionService(AbstractPermissionService):
    repository: PermissionRepository

    def __init__(self, *, repository: PermissionRepository) -> None:
        self.repository = repository

    async def get_list(self) -> Sequence[Permission]:
        return await self.repository.get_list()

    async def get(self, *, permission_id: uuid.UUID) -> Permission | None:
        return await self.repository.get(permission_id=permission_id)

    async def create(self, *, permission_create: PermissionCreate) -> Permission:
        return await self.repository.create(permission_create=permission_create)

    async def update(self, *, permission_id: uuid.UUID, permission_update: PermissionUpdate) -> Permission | None:
        await self.repository.update(permission_id=permission_id, permission_update=permission_update)
        return await self.repository.get(permission_id=permission_id)

    async def delete(self, *, permission_id: uuid.UUID) -> None:
        await self.repository.delete(permission_id=permission_id)


async def get_permission_service(repository: PermissionRepositoryDep) -> AbstractPermissionService:
    return PermissionService(repository=repository)


PermissionServiceDep = Annotated[AbstractPermissionService, Depends(get_permission_service)]

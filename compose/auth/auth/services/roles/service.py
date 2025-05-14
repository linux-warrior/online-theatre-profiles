from __future__ import annotations

import abc
import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from .models import (
    RoleCreate,
    RoleUpdate,
)
from .repository import (
    RoleRepository,
    RoleRepositoryDep,
)
from ...models.sqlalchemy import Role


class AbstractRoleService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self) -> Sequence[Role]: ...

    @abc.abstractmethod
    async def get(self, *, role_id: uuid.UUID) -> Role | None: ...

    @abc.abstractmethod
    async def create(self, *, role_create: RoleCreate) -> Role: ...

    @abc.abstractmethod
    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> Role | None: ...

    @abc.abstractmethod
    async def delete(self, *, role_id: uuid.UUID) -> None: ...


class RoleService(AbstractRoleService):
    repository: RoleRepository

    def __init__(self, *, repository: RoleRepository) -> None:
        self.repository = repository

    async def get_list(self) -> Sequence[Role]:
        return await self.repository.get_list()

    async def get(self, *, role_id: uuid.UUID) -> Role | None:
        return await self.repository.get(role_id=role_id)

    async def create(self, *, role_create: RoleCreate) -> Role:
        return await self.repository.create(role_create=role_create)

    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> Role | None:
        await self.repository.update(role_id=role_id, role_update=role_update)
        return await self.repository.get(role_id=role_id)

    async def delete(self, *, role_id: uuid.UUID) -> None:
        await self.repository.delete(role_id=role_id)


async def get_role_service(repository: RoleRepositoryDep) -> AbstractRoleService:
    return RoleService(repository=repository)


RoleServiceDep = Annotated[AbstractRoleService, Depends(get_role_service)]

from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends

from .models import (
    RoleRead,
    RoleCreate,
    RoleUpdate,
    RoleDelete,
)
from .repository import (
    RoleRepository,
    RoleRepositoryDep,
)


class AbstractRoleService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self) -> list[RoleRead]: ...

    @abc.abstractmethod
    async def get(self, *, role_id: uuid.UUID) -> RoleRead | None: ...

    @abc.abstractmethod
    async def create(self, *, role_create: RoleCreate) -> RoleRead: ...

    @abc.abstractmethod
    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> RoleRead | None: ...

    @abc.abstractmethod
    async def delete(self, *, role_id: uuid.UUID) -> RoleDelete | None: ...


class RoleService(AbstractRoleService):
    repository: RoleRepository

    def __init__(self, *, repository: RoleRepository) -> None:
        self.repository = repository

    async def get_list(self) -> list[RoleRead]:
        roles_list = await self.repository.get_list()

        return [
            RoleRead.model_validate(role, from_attributes=True)
            for role in roles_list
        ]

    async def get(self, *, role_id: uuid.UUID) -> RoleRead | None:
        role = await self.repository.get(role_id=role_id)

        if role is None:
            return None

        return RoleRead.model_validate(role, from_attributes=True)

    async def create(self, *, role_create: RoleCreate) -> RoleRead:
        role = await self.repository.create(role_create=role_create)
        return RoleRead.model_validate(role, from_attributes=True)

    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> RoleRead | None:
        rows_count = await self.repository.update(role_id=role_id, role_update=role_update)

        if not rows_count:
            return None

        return await self.get(role_id=role_id)

    async def delete(self, *, role_id: uuid.UUID) -> RoleDelete | None:
        rows_count = await self.repository.delete(role_id=role_id)

        if not rows_count:
            return None

        return RoleDelete(id=role_id)


async def get_role_service(repository: RoleRepositoryDep) -> AbstractRoleService:
    return RoleService(repository=repository)


RoleServiceDep = Annotated[AbstractRoleService, Depends(get_role_service)]

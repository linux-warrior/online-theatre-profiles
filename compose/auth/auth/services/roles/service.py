from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from .exceptions import DuplicateRoleTypeError
from .models import RoleCreateDto, RoleUpdateDto
from .repository import RoleRepository, RoleRepositoryDep
from ...models.sqlalchemy import Role


class RoleService:
    _repository: RoleRepository

    def __init__(self, repository: RoleRepository):
        self._repository = repository

    async def create(self, role_create: RoleCreateDto) -> Role:
        role_existed = await self._repository.get_by_code(role_create.code)
        if role_existed is not None:
            raise DuplicateRoleTypeError

        return await self._repository.create(role_create)

    async def update(self, id: uuid.UUID, role_update: RoleUpdateDto) -> Role | None:
        if role_update.code is not None:
            role = await self._repository.get_by_code(role_update.code)
            if role is not None and role.id != id:
                raise DuplicateRoleTypeError

        await self._repository.update(id, role_update)
        return await self._repository.get(id)

    async def delete(self, id: uuid.UUID) -> Role | None:
        role = await self._repository.get(id)
        if role is None:
            return None

        await self._repository.delete(id)
        return role

    async def get(self, id: uuid.UUID) -> Role | None:
        return await self._repository.get(id)

    async def get_list(self) -> Sequence[Role]:
        return await self._repository.get_list()


async def get_role_service(repository: RoleRepositoryDep) -> RoleService:
    return RoleService(repository)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]

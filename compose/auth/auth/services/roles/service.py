from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    RoleNotFound,
    RoleCreateError,
    RoleUpdateError,
)
from .models import (
    ReadRoleResponse,
    RoleCreate,
    RoleUpdate,
    DeleteRoleResponse,
)
from .repository import (
    RoleRepository,
    RoleRepositoryDep,
)
from ...models.schemas import (
    RoleSchema,
)
from ...models.sqlalchemy import (
    Role,
)


class AbstractRoleService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self) -> list[ReadRoleResponse]: ...

    @abc.abstractmethod
    async def get(self, *, role_id: uuid.UUID) -> ReadRoleResponse: ...

    @abc.abstractmethod
    async def create(self, *, role_create: RoleCreate) -> ReadRoleResponse: ...

    @abc.abstractmethod
    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> ReadRoleResponse: ...

    @abc.abstractmethod
    async def delete(self, *, role_id: uuid.UUID) -> DeleteRoleResponse: ...


class RoleService(AbstractRoleService):
    repository: RoleRepository

    def __init__(self, *, repository: RoleRepository) -> None:
        self.repository = repository

    async def get_list(self) -> list[ReadRoleResponse]:
        roles_list = await self.repository.get_list()

        return [self._get_read_role_response(role=role) for role in roles_list]

    async def get(self, *, role_id: uuid.UUID) -> ReadRoleResponse:
        role = await self.repository.get(role_id=role_id)

        if role is None:
            raise RoleNotFound

        return self._get_read_role_response(role=role)

    async def create(self, *, role_create: RoleCreate) -> ReadRoleResponse:
        try:
            role = await self.repository.create(role_create=role_create)
        except IntegrityError as e:
            raise RoleCreateError from e

        return self._get_read_role_response(role=role)

    async def update(self, *, role_id: uuid.UUID, role_update: RoleUpdate) -> ReadRoleResponse:
        try:
            update_role_result = await self.repository.update(role_id=role_id, role_update=role_update)
        except IntegrityError as e:
            raise RoleUpdateError from e

        if update_role_result is None:
            raise RoleNotFound

        return await self.get(role_id=role_id)

    async def delete(self, *, role_id: uuid.UUID) -> DeleteRoleResponse:
        delete_role_result = await self.repository.delete(role_id=role_id)

        if delete_role_result is None:
            raise RoleNotFound

        return DeleteRoleResponse(id=role_id)

    def _get_read_role_response(self, *, role: Role) -> ReadRoleResponse:
        role_schema = RoleSchema.model_validate(role, from_attributes=True)
        read_role_response_dict = role_schema.model_dump()

        return ReadRoleResponse.model_validate(read_role_response_dict)


async def get_role_service(repository: RoleRepositoryDep) -> AbstractRoleService:
    return RoleService(repository=repository)


RoleServiceDep = Annotated[AbstractRoleService, Depends(get_role_service)]

from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    UserRoleNotFound,
    UserRoleCreateError,
)
from .models import (
    ReadUserRoleResponse,
    DeleteUserRoleResponse,
)
from .repository import (
    UserRoleRepository,
    UserRoleRepositoryDep,
)


class AbstractUserRoleService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, *, user_id: uuid.UUID) -> list[ReadUserRoleResponse]: ...

    @abc.abstractmethod
    async def create(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> ReadUserRoleResponse: ...

    @abc.abstractmethod
    async def delete(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> DeleteUserRoleResponse: ...


class UserRoleService(AbstractUserRoleService):
    repository: UserRoleRepository

    def __init__(self, *, repository: UserRoleRepository) -> None:
        self.repository = repository

    async def get_list(self, *, user_id: uuid.UUID) -> list[ReadUserRoleResponse]:
        user_roles_list = await self.repository.get_list(user_id=user_id)

        return [
            ReadUserRoleResponse.model_validate(user_role, from_attributes=True)
            for user_role in user_roles_list
        ]

    async def create(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> ReadUserRoleResponse:
        try:
            user_role = await self.repository.create(user_id=user_id, role_id=role_id)
        except IntegrityError as e:
            raise UserRoleCreateError from e

        return ReadUserRoleResponse.model_validate(user_role, from_attributes=True)

    async def delete(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> DeleteUserRoleResponse:
        rows_count = await self.repository.delete(user_id=user_id, role_id=role_id)

        if not rows_count:
            raise UserRoleNotFound

        return DeleteUserRoleResponse(id=role_id)


async def get_user_role_service(repository: UserRoleRepositoryDep) -> AbstractUserRoleService:
    return UserRoleService(repository=repository)


UserRoleServiceDep = Annotated[AbstractUserRoleService, Depends(get_user_role_service)]

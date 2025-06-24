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
from ....models.schemas import (
    UserRoleSchema,
)
from ....models.sqlalchemy import (
    UserRole,
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

        return [self._get_read_user_role_response(user_role=user_role) for user_role in user_roles_list]

    async def create(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> ReadUserRoleResponse:
        try:
            user_role = await self.repository.create(user_id=user_id, role_id=role_id)
        except IntegrityError as e:
            raise UserRoleCreateError from e

        return self._get_read_user_role_response(user_role=user_role)

    async def delete(self, *, user_id: uuid.UUID, role_id: uuid.UUID) -> DeleteUserRoleResponse:
        delete_user_role_result = await self.repository.delete(user_id=user_id, role_id=role_id)

        if delete_user_role_result is None:
            raise UserRoleNotFound

        return DeleteUserRoleResponse(
            id=delete_user_role_result.id,
            user_id=delete_user_role_result.user_id,
            role_id=delete_user_role_result.role_id,
        )

    def _get_read_user_role_response(self, *, user_role: UserRole) -> ReadUserRoleResponse:
        user_role_schema = UserRoleSchema.model_validate(user_role, from_attributes=True)
        read_user_role_response_dict = user_role_schema.model_dump()

        return ReadUserRoleResponse.model_validate(read_user_role_response_dict)


async def get_user_role_service(repository: UserRoleRepositoryDep) -> AbstractUserRoleService:
    return UserRoleService(repository=repository)


UserRoleServiceDep = Annotated[AbstractUserRoleService, Depends(get_user_role_service)]

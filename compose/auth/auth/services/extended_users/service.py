from __future__ import annotations

import abc
from typing import Annotated

from fastapi import Depends

from .models import (
    ExtendedCurrentUserResponse,
    ExtendedReadUserResponse,
)
from .repository import (
    ExtendedUserRepository,
    ExtendedUserRepositoryDep,
)
from ...models.sqlalchemy import (
    User,
)


class AbstractExtendedUserService(abc.ABC):
    @abc.abstractmethod
    async def extend_current_user(self, *, user: User) -> ExtendedCurrentUserResponse: ...

    @abc.abstractmethod
    async def extend_user(self, *, user: User) -> ExtendedReadUserResponse: ...


class ExtendedUserService(AbstractExtendedUserService):
    repository: ExtendedUserRepository

    def __init__(self, *, repository: ExtendedUserRepository) -> None:
        self.repository = repository

    async def extend_current_user(self, *, user: User) -> ExtendedCurrentUserResponse:
        extended_current_user_response = ExtendedCurrentUserResponse.model_validate(
            user,
            from_attributes=True,
        )
        extended_current_user_response.permissions = await self.get_user_permissions(user=user)

        return extended_current_user_response

    async def extend_user(self, *, user: User) -> ExtendedReadUserResponse:
        extended_read_user_response = ExtendedReadUserResponse.model_validate(
            user,
            from_attributes=True,
        )
        extended_read_user_response.permissions = await self.get_user_permissions(user=user)

        return extended_read_user_response

    async def get_user_permissions(self, *, user: User) -> list[str]:
        permissions_list = await self.repository.get_user_permissions(user_id=user.id)

        return [permission.code for permission in permissions_list]


async def get_extended_user_service(repository: ExtendedUserRepositoryDep) -> AbstractExtendedUserService:
    return ExtendedUserService(repository=repository)


ExtendedUserServiceDep = Annotated[AbstractExtendedUserService, Depends(get_extended_user_service)]

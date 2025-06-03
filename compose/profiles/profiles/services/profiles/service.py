from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    ProfileNotFound,
    ProfileCreateError,
    ProfileUpdateError,
)
from .models import (
    ReadProfileResponse,
    ProfileCreate,
    ProfileUpdate,
    DeleteProfileResponse,
)
from .repository import (
    ProfileRepository,
    ProfileRepositoryDep,
)
from ..auth import (
    AbstractPermissionService,
    PermissionServiceDep,
    AbstractPermissionChecker,
)


class AbstractProfileService(abc.ABC):
    @abc.abstractmethod
    async def get(self, *, user_id: uuid.UUID) -> ReadProfileResponse: ...

    @abc.abstractmethod
    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     profile_create: ProfileCreate) -> ReadProfileResponse: ...

    @abc.abstractmethod
    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     profile_update: ProfileUpdate) -> ReadProfileResponse: ...

    @abc.abstractmethod
    async def delete(self, *, user_id: uuid.UUID) -> DeleteProfileResponse: ...


class ProfileService(AbstractProfileService):
    repository: ProfileRepository
    permission_checker: AbstractPermissionChecker

    def __init__(self,
                 *,
                 repository: ProfileRepository,
                 permission_service: AbstractPermissionService) -> None:
        self.repository = repository
        self.permission_checker = permission_service.get_permission_checker()

    async def get(self, *, user_id: uuid.UUID) -> ReadProfileResponse:
        await self.permission_checker.check_read_permission(user_id=user_id)

        profile = await self.repository.get(user_id=user_id)

        if profile is None:
            raise ProfileNotFound

        return ReadProfileResponse.model_validate(profile, from_attributes=True)

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     profile_create: ProfileCreate) -> ReadProfileResponse:
        await self.permission_checker.check_create_permission(user_id=user_id)

        try:
            profile = await self.repository.create(
                user_id=user_id,
                profile_create=profile_create,
            )

        except IntegrityError as e:
            raise ProfileCreateError from e

        return ReadProfileResponse.model_validate(profile, from_attributes=True)

    async def update(self,
                     *,
                     user_id: uuid.UUID,
                     profile_update: ProfileUpdate) -> ReadProfileResponse:
        await self.permission_checker.check_update_permission(user_id=user_id)

        try:
            rows_count = await self.repository.update(
                user_id=user_id,
                profile_update=profile_update,
            )

        except IntegrityError as e:
            raise ProfileUpdateError from e

        if not rows_count:
            raise ProfileNotFound

        return await self.get(user_id=user_id)

    async def delete(self, *, user_id: uuid.UUID) -> DeleteProfileResponse:
        await self.permission_checker.check_delete_permission(user_id=user_id)

        rows_count = await self.repository.delete(user_id=user_id)

        if not rows_count:
            raise ProfileNotFound

        return DeleteProfileResponse(user_id=user_id)


async def get_profile_service(repository: ProfileRepositoryDep,
                              permission_service: PermissionServiceDep) -> AbstractProfileService:
    return ProfileService(repository=repository, permission_service=permission_service)


ProfileServiceDep = Annotated[AbstractProfileService, Depends(get_profile_service)]

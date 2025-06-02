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

    def __init__(self, *, repository: ProfileRepository) -> None:
        self.repository = repository

    async def get(self, *, user_id: uuid.UUID) -> ReadProfileResponse:
        profile = await self.repository.get(user_id=user_id)

        if profile is None:
            raise ProfileNotFound

        return ReadProfileResponse.model_validate(profile, from_attributes=True)

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     profile_create: ProfileCreate) -> ReadProfileResponse:
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
        rows_count = await self.repository.delete(user_id=user_id)

        if not rows_count:
            raise ProfileNotFound

        return DeleteProfileResponse(user_id=user_id)


async def get_profile_service(repository: ProfileRepositoryDep) -> AbstractProfileService:
    return ProfileService(repository=repository)


ProfileServiceDep = Annotated[AbstractProfileService, Depends(get_profile_service)]

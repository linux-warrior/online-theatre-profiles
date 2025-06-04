from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    FavoriteNotFound,
    FavoriteCreateError,
)
from .models import (
    ReadFavoriteResponse,
    DeleteFavoriteResponse,
)
from .repository import (
    FavoriteRepository,
    FavoriteRepositoryDep,
)
from ..auth import (
    AbstractPermissionService,
    PermissionServiceDep,
    AbstractPermissionChecker,
)
from ...models.schemas import (
    FavoriteSchema,
)
from ...models.sqlalchemy import (
    Favorite,
)


class AbstractFavoriteService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, *, user_id: uuid.UUID) -> list[ReadFavoriteResponse]: ...

    @abc.abstractmethod
    async def create(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> ReadFavoriteResponse: ...

    @abc.abstractmethod
    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteFavoriteResponse: ...


class FavoriteService(AbstractFavoriteService):
    repository: FavoriteRepository
    permission_checker: AbstractPermissionChecker

    def __init__(self,
                 *,
                 repository: FavoriteRepository,
                 permission_service: AbstractPermissionService) -> None:
        self.repository = repository
        self.permission_checker = permission_service.get_permission_checker()

    async def get_list(self, *, user_id: uuid.UUID) -> list[ReadFavoriteResponse]:
        await self.permission_checker.check_read_permission(user_id=user_id)

        result_rows_list = await self.repository.get_list(user_id=user_id)

        return [self._get_read_favorite_response(
            favorite=result_row.Favorite,
            user_id=result_row.user_id,
        ) for result_row in result_rows_list]

    async def create(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> ReadFavoriteResponse:
        await self.permission_checker.check_create_permission(user_id=user_id)

        try:
            favorite = await self.repository.create(user_id=user_id, film_id=film_id)
        except IntegrityError as e:
            raise FavoriteCreateError from e

        return self._get_read_favorite_response(favorite=favorite, user_id=user_id)

    async def delete(self, *, user_id: uuid.UUID, film_id: uuid.UUID) -> DeleteFavoriteResponse:
        await self.permission_checker.check_delete_permission(user_id=user_id)

        rows_count = await self.repository.delete(user_id=user_id, film_id=film_id)

        if not rows_count:
            raise FavoriteNotFound

        return DeleteFavoriteResponse(user_id=user_id, film_id=film_id)

    def _get_read_favorite_response(self,
                                    *,
                                    favorite: Favorite,
                                    user_id: uuid.UUID) -> ReadFavoriteResponse:
        favorite_schema = FavoriteSchema.model_validate(favorite, from_attributes=True)
        read_favorite_response_dict = {
            **favorite_schema.model_dump(),
            'user_id': user_id,
        }

        return ReadFavoriteResponse.model_validate(read_favorite_response_dict)


async def get_favorite_service(repository: FavoriteRepositoryDep,
                               permission_service: PermissionServiceDep) -> AbstractFavoriteService:
    return FavoriteService(repository=repository, permission_service=permission_service)


FavoriteServiceDep = Annotated[AbstractFavoriteService, Depends(get_favorite_service)]

from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from ....services.auth import (
    CurrentUserDep,
)
from ....services.favorites import (
    FavoriteServiceDep,
    ReadFavoriteResponse,
    DeleteFavoriteResponse,
    FavoriteServiceException,
    FavoriteNotFound,
)

router = APIRouter()


@router.get(
    '/user/{user_id}/list',
    response_model=list[ReadFavoriteResponse],
    summary="Get a list of user's favorite films",
)
async def get_favorites_list(user_id: uuid.UUID,
                             favorite_service: FavoriteServiceDep,
                             _current_user: CurrentUserDep) -> list[ReadFavoriteResponse]:
    return await favorite_service.get_list(user_id=user_id)


@router.post(
    '/user/{user_id}/film/{film_id}',
    response_model=ReadFavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a film to a user's favorites",
)
async def add_user_role(user_id: uuid.UUID,
                        film_id: uuid.UUID,
                        favorite_service: FavoriteServiceDep,
                        _current_user: CurrentUserDep) -> ReadFavoriteResponse:
    try:
        return await favorite_service.create(
            user_id=user_id,
            film_id=film_id,
        )

    except FavoriteServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/user/{user_id}/film/{film_id}',
    response_model=DeleteFavoriteResponse,
    summary="Remove a film from a user's favorites",
)
async def remove_user_role(user_id: uuid.UUID,
                           film_id: uuid.UUID,
                           favorite_service: FavoriteServiceDep,
                           _current_user: CurrentUserDep) -> DeleteFavoriteResponse:
    try:
        return await favorite_service.delete(
            user_id=user_id,
            film_id=film_id,
        )

    except FavoriteNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

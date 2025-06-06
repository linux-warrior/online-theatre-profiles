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
from ....services.ratings import (
    RatingServiceDep,
    ReadRatingResponse,
    RatingCreate,
    RatingUpdate,
    DeleteRatingResponse,
    FilmRatingResponse,
    RatingServiceException,
    RatingNotFound,
)

router = APIRouter()


@router.get(
    '/user/{user_id}/list',
    response_model=list[ReadRatingResponse],
    summary='Get a list of user ratings',
)
async def get_ratings_list(user_id: uuid.UUID,
                           rating_service: RatingServiceDep,
                           _current_user: CurrentUserDep) -> list[ReadRatingResponse]:
    return await rating_service.get_list(user_id=user_id)


@router.get(
    '/user/{user_id}/film/{film_id}',
    response_model=ReadRatingResponse,
    summary='Get user rating details',
)
async def get_rating(user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     rating_service: RatingServiceDep,
                     _current_user: CurrentUserDep) -> ReadRatingResponse:
    try:
        return await rating_service.get(
            user_id=user_id,
            film_id=film_id,
        )

    except RatingNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    '/user/{user_id}/film/{film_id}',
    response_model=ReadRatingResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a user rating',
)
async def create_rating(user_id: uuid.UUID,
                        film_id: uuid.UUID,
                        rating_create: RatingCreate,
                        rating_service: RatingServiceDep,
                        _current_user: CurrentUserDep) -> ReadRatingResponse:
    try:
        return await rating_service.create(
            user_id=user_id,
            film_id=film_id,
            rating_create=rating_create,
        )

    except RatingServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    '/user/{user_id}/film/{film_id}',
    response_model=ReadRatingResponse,
    summary='Update a user rating',
)
async def update_rating(user_id: uuid.UUID,
                        film_id: uuid.UUID,
                        rating_update: RatingUpdate,
                        rating_service: RatingServiceDep,
                        _current_user: CurrentUserDep) -> ReadRatingResponse:
    try:
        return await rating_service.update(
            user_id=user_id,
            film_id=film_id,
            rating_update=rating_update,
        )

    except RatingNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except RatingServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/user/{user_id}/film/{film_id}',
    response_model=DeleteRatingResponse,
    summary='Delete a user rating',
)
async def delete_rating(user_id: uuid.UUID,
                        film_id: uuid.UUID,
                        rating_service: RatingServiceDep,
                        _current_user: CurrentUserDep) -> DeleteRatingResponse:
    try:
        return await rating_service.delete(
            user_id=user_id,
            film_id=film_id,
        )

    except RatingNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    '/film/{film_id}',
    response_model=FilmRatingResponse,
    summary='Get an aggregate user rating for a film',
)
async def get_film_rating(film_id: uuid.UUID,
                          rating_service: RatingServiceDep,
                          _current_user: CurrentUserDep) -> FilmRatingResponse:
    return await rating_service.get_for_film(film_id=film_id)

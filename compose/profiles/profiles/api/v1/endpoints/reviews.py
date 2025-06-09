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
from ....services.pagination import (
    PageParamsDep,
)
from ....services.reviews import (
    ReviewServiceDep,
    ReadReviewResponse,
    ReviewCreate,
    ReviewUpdate,
    DeleteReviewResponse,
    FilmReviewsResponse,
    ReviewServiceException,
    ReviewNotFound,
)

router = APIRouter()


@router.get(
    '/user/{user_id}/list',
    response_model=list[ReadReviewResponse],
    summary='Get a list of user reviews',
)
async def get_reviews_list(user_id: uuid.UUID,
                           page_params: PageParamsDep,
                           review_service: ReviewServiceDep,
                           _current_user: CurrentUserDep) -> list[ReadReviewResponse]:
    return await review_service.get_list(user_id=user_id, page_params=page_params)


@router.get(
    '/user/{user_id}/film/{film_id}',
    response_model=ReadReviewResponse,
    summary='Get user review details',
)
async def get_review(user_id: uuid.UUID,
                     film_id: uuid.UUID,
                     review_service: ReviewServiceDep,
                     _current_user: CurrentUserDep) -> ReadReviewResponse:
    try:
        return await review_service.get(
            user_id=user_id,
            film_id=film_id,
        )

    except ReviewNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    '/user/{user_id}/film/{film_id}',
    response_model=ReadReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a user review',
)
async def create_review(user_id: uuid.UUID,
                        film_id: uuid.UUID,
                        review_create: ReviewCreate,
                        review_service: ReviewServiceDep,
                        _current_user: CurrentUserDep) -> ReadReviewResponse:
    try:
        return await review_service.create(
            user_id=user_id,
            film_id=film_id,
            review_create=review_create,
        )

    except ReviewServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    '/user/{user_id}/film/{film_id}',
    response_model=ReadReviewResponse,
    summary='Update a user review',
)
async def update_review(user_id: uuid.UUID,
                        film_id: uuid.UUID,
                        review_update: ReviewUpdate,
                        review_service: ReviewServiceDep,
                        _current_user: CurrentUserDep) -> ReadReviewResponse:
    try:
        return await review_service.update(
            user_id=user_id,
            film_id=film_id,
            review_update=review_update,
        )

    except ReviewNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ReviewServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/user/{user_id}/film/{film_id}',
    response_model=DeleteReviewResponse,
    summary='Delete a user review',
)
async def delete_review(user_id: uuid.UUID,
                        film_id: uuid.UUID,
                        review_service: ReviewServiceDep,
                        _current_user: CurrentUserDep) -> DeleteReviewResponse:
    try:
        return await review_service.delete(
            user_id=user_id,
            film_id=film_id,
        )

    except ReviewNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    '/film/{film_id}',
    response_model=FilmReviewsResponse,
    summary='Get user reviews for a film',
)
async def get_film_reviews(film_id: uuid.UUID,
                           page_params: PageParamsDep,
                           review_service: ReviewServiceDep,
                           _current_user: CurrentUserDep) -> FilmReviewsResponse:
    return await review_service.get_film_reviews(film_id=film_id, page_params=page_params)

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
from ....services.profiles import (
    ProfileServiceDep,
    ReadProfileResponse,
    ProfileCreate,
    ProfileUpdate,
    DeleteProfileResponse,
    ProfileNotFound,
    ProfileServiceException,
)

router = APIRouter()


@router.get(
    '/user/{user_id}',
    response_model=ReadProfileResponse,
    summary='Get user profile details',
)
async def get_profile(user_id: uuid.UUID,
                      profile_service: ProfileServiceDep,
                      _current_user: CurrentUserDep) -> ReadProfileResponse:
    try:
        return await profile_service.get(user_id=user_id)

    except ProfileNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    '/user/{user_id}',
    response_model=ReadProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new user profile',
)
async def create_profile(user_id: uuid.UUID,
                         profile_create: ProfileCreate,
                         profile_service: ProfileServiceDep,
                         _current_user: CurrentUserDep) -> ReadProfileResponse:
    try:
        return await profile_service.create(
            user_id=user_id,
            profile_create=profile_create,
        )

    except ProfileServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    '/user/{user_id}',
    response_model=ReadProfileResponse,
    summary='Update an existing user profile',
)
async def update_profile(user_id: uuid.UUID,
                         profile_update: ProfileUpdate,
                         profile_service: ProfileServiceDep,
                         _current_user: CurrentUserDep) -> ReadProfileResponse:
    try:
        return await profile_service.update(
            user_id=user_id,
            profile_update=profile_update,
        )

    except ProfileNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ProfileServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/user/{user_id}',
    response_model=DeleteProfileResponse,
    summary='Delete a user profile',
)
async def delete_profile(user_id: uuid.UUID,
                         profile_service: ProfileServiceDep,
                         _current_user: CurrentUserDep) -> DeleteProfileResponse:
    try:
        return await profile_service.delete(user_id=user_id)

    except ProfileNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

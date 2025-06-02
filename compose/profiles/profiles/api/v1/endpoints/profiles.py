from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

router = APIRouter()

from ....services.profiles import (
    ProfileServiceDep,
    ReadProfileResponse,
    ProfileCreate,
    ProfileUpdate,
    DeleteProfileResponse,
    ProfileNotFound,
    ProfileServiceException,
)


@router.get(
    '/{user_id}',
    response_model=ReadProfileResponse,
    summary='Get profile details',
)
async def get_profile(user_id: uuid.UUID,
                      profile_service: ProfileServiceDep) -> ReadProfileResponse:
    try:
        return await profile_service.get(user_id=user_id)

    except ProfileNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    '/{user_id}',
    response_model=ReadProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new profile',
)
async def create_profile(user_id: uuid.UUID,
                         profile_create: ProfileCreate,
                         profile_service: ProfileServiceDep) -> ReadProfileResponse:
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
    '/{user_id}',
    response_model=ReadProfileResponse,
    summary='Update an existing profile',
)
async def update_profile(user_id: uuid.UUID,
                         profile_update: ProfileUpdate,
                         profile_service: ProfileServiceDep) -> ReadProfileResponse:
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
    '/{user_id}',
    response_model=DeleteProfileResponse,
    summary='Delete a profile',
)
async def delete_profile(user_id: uuid.UUID,
                         profile_service: ProfileServiceDep) -> DeleteProfileResponse:
    try:
        return await profile_service.delete(user_id=user_id)

    except ProfileNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

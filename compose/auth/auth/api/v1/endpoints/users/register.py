from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from .....services.extended_users import (
    ExtendedUserServiceDep,
    ExtendedCurrentUserResponse,
)
from .....services.users import (
    UserManagerDep,
    UserCreate,
    UserAlreadyExists,
)

router = APIRouter()


@router.post(
    '/register',
    response_model=ExtendedCurrentUserResponse,
    status_code=status.HTTP_201_CREATED,
    name='register:register',
)
async def register(user_create: UserCreate,
                   user_manager: UserManagerDep,
                   ext_user_service: ExtendedUserServiceDep) -> ExtendedCurrentUserResponse:
    try:
        user = await user_manager.create(user_create=user_create)

    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return await ext_user_service.extend_current_user(user=user)

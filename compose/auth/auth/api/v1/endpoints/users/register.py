from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from .....services.extended_users import (
    ExtendedCurrentUserResponse,
)
from .....services.users import (
    UserServiceDep,
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
                   user_service: UserServiceDep) -> ExtendedCurrentUserResponse:
    try:
        return await user_service.register(user_create=user_create)

    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

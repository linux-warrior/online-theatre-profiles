from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from .common import ErrorCode, ErrorModel
from .....services.users import (
    UserManagerDep,
    UserRead,
    UserCreate,
    UserAlreadyExists,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    name="register:register",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this login already exists.",
                            "value": {
                                "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                            },
                        },
                    }
                }
            },
        },
    },
)
async def register(user_create: UserCreate, user_manager: UserManagerDep):
    try:
        created_user = await user_manager.create(user_create)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )

    return UserRead.model_validate(created_user, from_attributes=True)

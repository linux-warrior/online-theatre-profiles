from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from .common import ErrorCode, ErrorModel
from .....services.users import (
    CurrentUserDep,
    CurrentSuperuserDep,
    UserManagerDep,
    UserDoesNotExist,
    UserAlreadyExists,
    ReadUserResponse,
    UserUpdate,
    ExtendedReadUserResponse,
)
from .....services.users.authentication.login_history.dependencies import PageDep
from .....services.users.authentication.login_history.models import LoginHistoryInDb
from .....services.users.authentication.login_history.service import LoginHistoryServiceDep

router = APIRouter()


@router.get(
    '/profile',
    name='users:current_user',
    response_model=ReadUserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Token is invalid or missing.',
        },
    },
)
async def get_current_user(user: CurrentUserDep) -> ReadUserResponse:
    return ReadUserResponse.model_validate(user, from_attributes=True)


@router.patch(
    '/profile',
    name='users:patch_current_user',
    response_model=ReadUserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Token is invalid or missing.',
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': ErrorModel,
            'content': {
                'application/json': {
                    'examples': {
                        ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS: {
                            'summary': 'A user with this login already exists.',
                            'value': {
                                'detail': ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS
                            },
                        },
                    }
                }
            },
        },
    },
)
async def patch_current_user(user: CurrentUserDep,
                             user_update: UserUpdate,
                             user_manager: UserManagerDep) -> ReadUserResponse:
    try:
        user = await user_manager.update(user_update, user)
    except UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS,
        )

    return ReadUserResponse.model_validate(user, from_attributes=True)


@router.get(
    '/{user_id}/profile',
    name='users:user',
    response_model=ExtendedReadUserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Missing token or inactive user.',
        },
        status.HTTP_403_FORBIDDEN: {
            'description': 'Not a superuser.',
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'The user does not exist.',
        },
    },
)
async def get_user(user_id: uuid.UUID,
                   user_manager: UserManagerDep,
                   _current_superuser: CurrentSuperuserDep) -> ExtendedReadUserResponse:
    try:
        user = await user_manager.get(user_id)
    except UserDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorCode.USER_DOES_NOT_EXIST,
        )

    return ExtendedReadUserResponse.model_validate(user, from_attributes=True)


@router.get(
    '/list',
    name='users:users-list',
    response_model=list[ExtendedReadUserResponse],
)
async def get_users_list(*,
                         user_id: uuid.UUID | None = None,
                         user_created: datetime.datetime | None = None,
                         page_size: Annotated[int, Query(ge=1, le=100)] = 100,
                         user_manager: UserManagerDep,
                         _current_superuser: CurrentSuperuserDep) -> list[ExtendedReadUserResponse]:
    users_list = await user_manager.get_list(
        id=user_id,
        created=user_created,
        count=page_size,
    )

    return [
        ExtendedReadUserResponse.model_validate(user, from_attributes=True)
        for user in users_list
    ]


@router.get(
    '/get_login_history',
    name='users:history_login_current_user',
    response_model=list[LoginHistoryInDb],
    status_code=status.HTTP_200_OK,
)
async def get_login_history(
        login_history_service: LoginHistoryServiceDep,
        page: PageDep,
        user: CurrentUserDep,
):
    login_history_list = await login_history_service.get_list(user.id, page)
    return [
        LoginHistoryInDb.model_validate(login_history, from_attributes=True)
        for login_history in login_history_list
    ]

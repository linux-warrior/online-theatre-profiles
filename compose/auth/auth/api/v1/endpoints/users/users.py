from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from .common import ErrorCode, ErrorModel
from .....services.extended_users import (
    ExtendedUserServiceDep,
    ExtendedCurrentUserResponse,
    ExtendedReadUserResponse,
)
from .....services.pagination import (
    PageParamsDep,
)
from .....services.users import (
    CurrentUserDep,
    CurrentSuperuserDep,
    UserManagerDep,
    UserDoesNotExist,
    UserAlreadyExists,
    ReadUserResponse,
    UserUpdate,
)
from .....services.users.login_history import (
    LoginHistoryServiceDep,
    ReadLoginHistoryResponse,
)

router = APIRouter()


@router.get(
    '/profile',
    name='users:current_user',
    response_model=ExtendedCurrentUserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Token is invalid or missing.',
        },
    },
)
async def get_current_user(user: CurrentUserDep,
                           ext_user_service: ExtendedUserServiceDep) -> ExtendedCurrentUserResponse:
    return await ext_user_service.extend_current_user(user=user)


@router.patch(
    '/profile',
    name='users:patch_current_user',
    response_model=ExtendedCurrentUserResponse,
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
                             user_manager: UserManagerDep,
                             ext_user_service: ExtendedUserServiceDep) -> ExtendedCurrentUserResponse:
    try:
        user = await user_manager.update(user_update, user)

    except UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_LOGIN_ALREADY_EXISTS,
        )

    return await ext_user_service.extend_current_user(user=user)


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
                   ext_user_service: ExtendedUserServiceDep,
                   _current_superuser: CurrentSuperuserDep) -> ExtendedReadUserResponse:
    try:
        user = await user_manager.get(user_id)

    except UserDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorCode.USER_DOES_NOT_EXIST,
        )

    return await ext_user_service.extend_user(user=user)


@router.get(
    '/list',
    name='users:users_list',
    response_model=list[ReadUserResponse],
)
async def get_users_list(*,
                         page_params: PageParamsDep,
                         user_manager: UserManagerDep,
                         _current_superuser: CurrentSuperuserDep) -> list[ReadUserResponse]:
    users_list = await user_manager.get_list(page_params=page_params)

    return [
        ReadUserResponse.model_validate(user, from_attributes=True)
        for user in users_list
    ]


@router.get(
    '/login-history',
    name='users:current_user_login_history',
    response_model=list[ReadLoginHistoryResponse],
)
async def get_login_history_list(user: CurrentUserDep,
                                 page_params: PageParamsDep,
                                 login_history_service: LoginHistoryServiceDep) -> list[ReadLoginHistoryResponse]:
    return await login_history_service.get_list(user_id=user.id, page_params=page_params)

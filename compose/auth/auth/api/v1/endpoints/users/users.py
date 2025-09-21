from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from .....services.extended_users import (
    ExtendedCurrentUserResponse,
    ExtendedReadUserResponse,
)
from .....services.pagination import (
    PageParamsDep,
)
from .....services.users import (
    UserServiceDep,
    CurrentUserDep,
    CurrentSuperuserDep,
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
                           user_service: UserServiceDep) -> ExtendedCurrentUserResponse:
    return await user_service.get_current_user(user=user)


@router.patch(
    '/profile',
    name='users:patch_current_user',
    response_model=ExtendedCurrentUserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Token is invalid or missing.',
        },
    },
)
async def patch_current_user(user: CurrentUserDep,
                             user_update: UserUpdate,
                             user_service: UserServiceDep) -> ExtendedCurrentUserResponse:
    try:
        return await user_service.patch_current_user(user=user, user_update=user_update)

    except UserDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


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
                   user_service: UserServiceDep,
                   _current_superuser: CurrentSuperuserDep) -> ExtendedReadUserResponse:
    try:
        return await user_service.get_user(user_id=user_id)

    except UserDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    '/list',
    name='users:users_list',
    response_model=list[ReadUserResponse],
)
async def get_users_list(*,
                         page_params: PageParamsDep,
                         user_service: UserServiceDep,
                         _current_superuser: CurrentSuperuserDep) -> list[ReadUserResponse]:
    return await user_service.get_users_list(page_params=page_params)


@router.get(
    '/login-history',
    name='users:current_user_login_history',
    response_model=list[ReadLoginHistoryResponse],
)
async def get_login_history_list(user: CurrentUserDep,
                                 page_params: PageParamsDep,
                                 login_history_service: LoginHistoryServiceDep) -> list[ReadLoginHistoryResponse]:
    return await login_history_service.get_list(user_id=user.id, page_params=page_params)

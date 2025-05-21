from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from .....services.roles.user_roles import (
    UserRoleServiceDep,
    UserRoleRead,
    UserRoleDelete,
    UserRoleServiceException,
    UserRoleNotFound,
)
from .....services.users import CurrentSuperuserDep

router = APIRouter()


@router.get(
    '/user/{user_id}/list',
    response_model=list[UserRoleRead],
    summary='Get a list of user roles',
)
async def get_user_roles_list(user_id: uuid.UUID,
                              user_role_service: UserRoleServiceDep,
                              _current_superuser: CurrentSuperuserDep) -> list[UserRoleRead]:
    return await user_role_service.get_list(user_id=user_id)


@router.post(
    '/user/{user_id}/add/{role_id}',
    response_model=UserRoleRead,
    status_code=status.HTTP_201_CREATED,
    summary='Add a role to a user',
)
async def add_user_role(user_id: uuid.UUID,
                        role_id: uuid.UUID,
                        user_role_service: UserRoleServiceDep,
                        _current_superuser: CurrentSuperuserDep) -> UserRoleRead:
    try:
        return await user_role_service.create(
            user_id=user_id,
            role_id=role_id,
        )

    except UserRoleServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/user/{user_id}/remove/{role_id}',
    response_model=UserRoleDelete,
    summary='Remove a role from a user',
)
async def remove_user_role(user_id: uuid.UUID,
                           role_id: uuid.UUID,
                           user_role_service: UserRoleServiceDep,
                           _current_superuser: CurrentSuperuserDep) -> UserRoleDelete:
    try:
        return await user_role_service.delete(
            user_id=user_id,
            role_id=role_id,
        )

    except UserRoleNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

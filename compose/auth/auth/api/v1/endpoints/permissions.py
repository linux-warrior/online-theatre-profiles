from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import (
    APIRouter,
    HTTPException
)

from ....services.base.exceptions import (
    AddError,
    DeleteError
)
from ....services.permissions.exceptions import DuplicateUserPermissionError
from ....services.permissions.models import (
    CreatePermissionDto,
    PermissionInDb,
    DeletePermission
)
from ....services.permissions.service import PermissionServiceDep
from ....services.users import CurrentSuperuserDep

router = APIRouter()


@router.post(
    '/assign',
    response_model=PermissionInDb,
    status_code=HTTPStatus.CREATED,
    summary='Assign permission',
    description='Addition user into role'
)
async def assign(
        permission: CreatePermissionDto,
        permission_service: PermissionServiceDep,
        _superuser: CurrentSuperuserDep
) -> PermissionInDb:
    try:
        user_role = await permission_service.assign(permission)
    except DuplicateUserPermissionError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Duplicate permission'
        )
    except AddError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Add error'
        )

    return PermissionInDb.model_validate(user_role, from_attributes=True)


@router.get(
    '/get_by_user/{user_id}',
    response_model=list[PermissionInDb],
    status_code=HTTPStatus.OK,
    summary='Get permissions',
    description='Get list of roles for user'
)
async def get_by_user(
        user_id: uuid.UUID,
        permission_service: PermissionServiceDep,
        _superuser: CurrentSuperuserDep
) -> list[PermissionInDb]:
    user_roles_list = await permission_service.get_by_user(user_id)
    return [
        PermissionInDb.model_validate(user_role, from_attributes=True)
        for user_role in user_roles_list
    ]


@router.delete(
    '/revoke/{id}',
    response_model=DeletePermission,
    status_code=HTTPStatus.OK,
    summary='Revoke permissions',
    description='Deleting user from role'
)
async def revoke(
        id: uuid.UUID,
        permission_service: PermissionServiceDep,
        _superuser: CurrentSuperuserDep
) -> DeletePermission:
    try:
        user_role = await permission_service.revoke(id)
    except DeleteError:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Delete error'
        )

    if user_role is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Permission not found'
        )

    return DeletePermission.model_validate(user_role, from_attributes=True)

from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from .....services.permissions.role_permissions import (
    RolePermissionServiceDep,
    RolePermissionRead,
    RolePermissionDelete,
    RolePermissionServiceException,
    RolePermissionNotFound,
)
from .....services.users import CurrentSuperuserDep

router = APIRouter()


@router.get(
    '/role/{role_id}/list',
    response_model=list[RolePermissionRead],
    summary='Get a list of role permissions',
)
async def get_role_permissions_list(role_id: uuid.UUID,
                                    role_permission_service: RolePermissionServiceDep,
                                    _current_superuser: CurrentSuperuserDep) -> list[RolePermissionRead]:
    return await role_permission_service.get_list(role_id=role_id)


@router.post(
    '/role/{role_id}/add/{permission_id}',
    response_model=RolePermissionRead,
    status_code=status.HTTP_201_CREATED,
    summary='Add a permission to a role',
)
async def add_role_permission(role_id: uuid.UUID,
                              permission_id: uuid.UUID,
                              role_permission_service: RolePermissionServiceDep,
                              _current_superuser: CurrentSuperuserDep) -> RolePermissionRead:
    try:
        return await role_permission_service.create(
            role_id=role_id,
            permission_id=permission_id,
        )

    except RolePermissionServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/role/{role_id}/remove/{permission_id}',
    response_model=RolePermissionDelete,
    summary='Remove a permission from a role',
)
async def remove_role_permission(role_id: uuid.UUID,
                                 permission_id: uuid.UUID,
                                 role_permission_service: RolePermissionServiceDep,
                                 _current_superuser: CurrentSuperuserDep) -> RolePermissionDelete:
    try:
        return await role_permission_service.delete(
            role_id=role_id,
            permission_id=permission_id,
        )

    except RolePermissionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

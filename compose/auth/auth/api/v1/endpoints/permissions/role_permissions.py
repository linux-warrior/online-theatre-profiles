from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from .....services.pagination import (
    PageParamsDep,
)
from .....services.permissions.role_permissions import (
    RolePermissionServiceDep,
    ReadRolePermissionResponse,
    DeleteRolePermissionResponse,
    RolePermissionServiceException,
    RolePermissionNotFound,
)
from .....services.users import CurrentSuperuserDep

router = APIRouter()


@router.get(
    '/role/{role_id}/list',
    response_model=list[ReadRolePermissionResponse],
    summary='Get a list of role permissions',
)
async def get_role_permissions_list(role_id: uuid.UUID,
                                    page_params: PageParamsDep,
                                    role_permission_service: RolePermissionServiceDep,
                                    _current_superuser: CurrentSuperuserDep) -> list[ReadRolePermissionResponse]:
    return await role_permission_service.get_list(role_id=role_id, page_params=page_params)


@router.post(
    '/role/{role_id}/permission/{permission_id}',
    response_model=ReadRolePermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Add a permission to a role',
)
async def add_role_permission(role_id: uuid.UUID,
                              permission_id: uuid.UUID,
                              role_permission_service: RolePermissionServiceDep,
                              _current_superuser: CurrentSuperuserDep) -> ReadRolePermissionResponse:
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
    '/role/{role_id}/permission/{permission_id}',
    response_model=DeleteRolePermissionResponse,
    summary='Remove a permission from a role',
)
async def remove_role_permission(role_id: uuid.UUID,
                                 permission_id: uuid.UUID,
                                 role_permission_service: RolePermissionServiceDep,
                                 _current_superuser: CurrentSuperuserDep) -> DeleteRolePermissionResponse:
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

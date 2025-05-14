from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from ....services.permissions import (
    PermissionServiceDep,
    PermissionRead,
    PermissionCreate,
    PermissionUpdate,
    PermissionDelete,
)
from ....services.users import CurrentSuperuserDep

router = APIRouter()


@router.get(
    '/list',
    response_model=list[PermissionRead],
    summary='Get a list of permissions',
)
async def get_permissions_list(permission_service: PermissionServiceDep,
                               _current_superuser: CurrentSuperuserDep) -> list[PermissionRead]:
    permissions_list = await permission_service.get_list()

    return [
        PermissionRead.model_validate(permission, from_attributes=True)
        for permission in permissions_list
    ]


@router.get(
    '/get/{permission_id}',
    response_model=PermissionRead,
    summary='Get permission details',
)
async def get_permission(permission_id: uuid.UUID,
                         permission_service: PermissionServiceDep,
                         _current_superuser: CurrentSuperuserDep) -> PermissionRead:
    permission = await permission_service.get(permission_id=permission_id)

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Permission not found',
        )

    return PermissionRead.model_validate(permission, from_attributes=True)


@router.post(
    '/create',
    response_model=PermissionRead,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new permission',
)
async def create_permission(permission_create: PermissionCreate,
                            permission_service: PermissionServiceDep,
                            _current_superuser: CurrentSuperuserDep) -> PermissionRead:
    permission = await permission_service.create(permission_create=permission_create)

    return PermissionRead.model_validate(permission, from_attributes=True)


@router.patch(
    '/update/{permission_id}',
    response_model=PermissionRead,
    summary='Update an existing permission',
)
async def update_permission(permission_id: uuid.UUID,
                            permission_update: PermissionUpdate,
                            permission_service: PermissionServiceDep,
                            _current_superuser: CurrentSuperuserDep) -> PermissionRead:
    permission = await permission_service.update(permission_id=permission_id, permission_update=permission_update)

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Permission not found',
        )

    return PermissionRead.model_validate(permission, from_attributes=True)


@router.delete(
    '/delete/{permission_id}',
    response_model=PermissionDelete,
    summary='Delete a permission',
)
async def delete_permission(permission_id: uuid.UUID,
                            permission_service: PermissionServiceDep,
                            _current_superuser: CurrentSuperuserDep) -> PermissionDelete:
    await permission_service.delete(permission_id=permission_id)

    return PermissionDelete(id=permission_id)

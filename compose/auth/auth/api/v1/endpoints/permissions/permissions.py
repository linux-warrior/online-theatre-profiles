from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from .....services.permissions import (
    PermissionServiceDep,
    ReadPermissionResponse,
    PermissionCreate,
    PermissionUpdate,
    DeletePermissionResponse,
    PermissionNotFound,
    PermissionServiceException,
)
from .....services.users import (
    CurrentSuperuserDep,
)

router = APIRouter()


@router.get(
    '/list',
    response_model=list[ReadPermissionResponse],
    summary='Get a list of permissions',
)
async def get_permissions_list(permission_service: PermissionServiceDep,
                               _current_superuser: CurrentSuperuserDep) -> list[ReadPermissionResponse]:
    return await permission_service.get_list()


@router.get(
    '/{permission_id}',
    response_model=ReadPermissionResponse,
    summary='Get permission details',
)
async def get_permission(permission_id: uuid.UUID,
                         permission_service: PermissionServiceDep,
                         _current_superuser: CurrentSuperuserDep) -> ReadPermissionResponse:
    try:
        return await permission_service.get(permission_id=permission_id)

    except PermissionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    '/create',
    response_model=ReadPermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new permission',
)
async def create_permission(permission_create: PermissionCreate,
                            permission_service: PermissionServiceDep,
                            _current_superuser: CurrentSuperuserDep) -> ReadPermissionResponse:
    try:
        return await permission_service.create(permission_create=permission_create)

    except PermissionServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    '/{permission_id}',
    response_model=ReadPermissionResponse,
    summary='Update an existing permission',
)
async def update_permission(permission_id: uuid.UUID,
                            permission_update: PermissionUpdate,
                            permission_service: PermissionServiceDep,
                            _current_superuser: CurrentSuperuserDep) -> ReadPermissionResponse:
    try:
        return await permission_service.update(
            permission_id=permission_id,
            permission_update=permission_update,
        )

    except PermissionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except PermissionServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/{permission_id}',
    response_model=DeletePermissionResponse,
    summary='Delete a permission',
)
async def delete_permission(permission_id: uuid.UUID,
                            permission_service: PermissionServiceDep,
                            _current_superuser: CurrentSuperuserDep) -> DeletePermissionResponse:
    try:
        return await permission_service.delete(permission_id=permission_id)

    except PermissionServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

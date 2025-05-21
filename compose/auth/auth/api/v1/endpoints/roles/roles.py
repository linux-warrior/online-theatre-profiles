from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from .....services.roles import (
    RoleServiceDep,
    RoleRead,
    RoleCreate,
    RoleUpdate,
    RoleDelete,
    RoleNotFound,
    RoleServiceException,
)
from .....services.users import CurrentSuperuserDep

router = APIRouter()


@router.get(
    '/list',
    response_model=list[RoleRead],
    summary='Get a list of roles',
)
async def get_roles_list(role_service: RoleServiceDep,
                         _current_superuser: CurrentSuperuserDep) -> list[RoleRead]:
    return await role_service.get_list()


@router.get(
    '/get/{role_id}',
    response_model=RoleRead,
    summary='Get role details',
)
async def get_role(role_id: uuid.UUID,
                   role_service: RoleServiceDep,
                   _current_superuser: CurrentSuperuserDep) -> RoleRead:
    try:
        return await role_service.get(role_id=role_id)

    except RoleNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    '/create',
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new role',
)
async def create_role(role_create: RoleCreate,
                      role_service: RoleServiceDep,
                      _current_superuser: CurrentSuperuserDep) -> RoleRead:
    try:
        return await role_service.create(role_create=role_create)

    except RoleServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    '/update/{role_id}',
    response_model=RoleRead,
    summary='Update an existing role',
)
async def update_role(role_id: uuid.UUID,
                      role_update: RoleUpdate,
                      role_service: RoleServiceDep,
                      _current_superuser: CurrentSuperuserDep) -> RoleRead:
    try:
        return await role_service.update(
            role_id=role_id,
            role_update=role_update,
        )

    except RoleNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except RoleServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    '/delete/{role_id}',
    response_model=RoleDelete,
    summary='Delete a role',
)
async def delete_role(role_id: uuid.UUID,
                      role_service: RoleServiceDep,
                      _current_superuser: CurrentSuperuserDep) -> RoleDelete:
    try:
        return await role_service.delete(role_id=role_id)

    except RoleNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from ....services.roles import (
    RoleServiceDep,
    RoleRead,
    RoleCreate,
    RoleUpdate,
    RoleDelete,
)
from ....services.users import CurrentSuperuserDep

router = APIRouter()


@router.get(
    '/list',
    response_model=list[RoleRead],
    summary='Get a list of roles',
)
async def get_roles_list(role_service: RoleServiceDep,
                         _current_superuser: CurrentSuperuserDep) -> list[RoleRead]:
    roles_list = await role_service.get_list()

    return [
        RoleRead.model_validate(role, from_attributes=True)
        for role in roles_list
    ]


@router.get(
    '/get/{role_id}',
    response_model=RoleRead,
    summary='Get role details',
)
async def get_role(role_id: uuid.UUID,
                   role_service: RoleServiceDep,
                   _current_superuser: CurrentSuperuserDep) -> RoleRead:
    role = await role_service.get(role_id=role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Role not found',
        )

    return RoleRead.model_validate(role, from_attributes=True)


@router.post(
    '/create',
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new role',
)
async def create_role(role_create: RoleCreate,
                      role_service: RoleServiceDep,
                      _current_superuser: CurrentSuperuserDep) -> RoleRead:
    role = await role_service.create(role_create=role_create)

    return RoleRead.model_validate(role, from_attributes=True)


@router.patch(
    '/update/{role_id}',
    response_model=RoleRead,
    summary='Update an existing role',
)
async def update_role(role_id: uuid.UUID,
                      role_update: RoleUpdate,
                      role_service: RoleServiceDep,
                      _current_superuser: CurrentSuperuserDep) -> RoleRead:
    role = await role_service.update(role_id=role_id, role_update=role_update)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Role not found',
        )

    return RoleRead.model_validate(role, from_attributes=True)


@router.delete(
    '/delete/{role_id}',
    response_model=RoleDelete,
    summary='Delete a role',
)
async def delete_role(role_id: uuid.UUID,
                      role_service: RoleServiceDep,
                      _current_superuser: CurrentSuperuserDep) -> RoleDelete:
    await role_service.delete(role_id=role_id)

    return RoleDelete(id=role_id)

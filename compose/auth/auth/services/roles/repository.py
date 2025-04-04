from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError

from .models import RoleCreateDto, RoleUpdateDto
from ..base.exceptions import AddError, DeleteError, UpdateError
from ...db.sqlalchemy import AsyncSession, AsyncSessionDep
from ...models.sqlalchemy import Role


class RoleRepository:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, role_create: RoleCreateDto) -> Role:
        role_dto = jsonable_encoder(role_create)
        role = Role(**role_dto)
        self._db.add(role)

        try:
            await self._db.commit()
            await self._db.refresh(role)
        except SQLAlchemyError:
            await self._db.rollback()
            raise AddError

        return role

    async def update(self, id: uuid.UUID, role_update: RoleUpdateDto):
        fields = role_update.model_dump(exclude_unset=True)
        statement = update(Role).where(Role.id == id).values(fields)

        try:
            await self._db.execute(statement)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise UpdateError

    async def get_by_code(self, code: str) -> Role | None:
        statement = select(Role).where(Role.code == code)
        result = await self._db.execute(statement)
        return result.scalar_one_or_none()

    async def get(self, id: uuid.UUID) -> Role | None:
        statement = select(Role).where(Role.id == id)
        result = await self._db.execute(statement)
        return result.scalar_one_or_none()

    async def get_list(self) -> Sequence[Role]:
        statement = select(Role)
        result = await self._db.execute(statement)
        return result.scalars().all()

    async def delete(self, id: uuid.UUID):
        query = delete(Role).where(Role.id == id)

        try:
            await self._db.execute(query)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise DeleteError


async def get_role_repository(db: AsyncSessionDep):
    return RoleRepository(db)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]

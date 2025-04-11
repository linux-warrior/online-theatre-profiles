from __future__ import annotations

import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils.auth.sqlalchemy import Role


@pytest_asyncio.fixture(scope='module')
async def create_role(async_session: AsyncSession):
    new_role = Role(name='subscribers', code='subscribers')
    async_session.add(new_role)
    await async_session.commit()
    await async_session.refresh(new_role)

    yield new_role

    await async_session.execute(delete(Role).where(Role.id == new_role.id))
    await async_session.commit()

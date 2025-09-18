from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import AbstractUserDatabase
from .db import UserDatabase
from ...pagination import (
    PaginationServiceDep,
)
from ....db.sqlalchemy import AsyncSessionDep


async def get_user_database(session: AsyncSessionDep,
                            pagination_service: PaginationServiceDep) -> AbstractUserDatabase:
    return UserDatabase(
        session=session,
        pagination_service=pagination_service,
    )


UserDatabaseDep = Annotated[AbstractUserDatabase, Depends(get_user_database)]

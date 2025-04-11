from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import BaseUserDatabase
from .sqlalchemy import SQLAlchemyUserDatabase
from ....db.sqlalchemy import AsyncSessionDep
from ....models.sqlalchemy import (
    User,
    OAuthAccount,
)


async def get_user_database(session: AsyncSessionDep) -> BaseUserDatabase:
    return SQLAlchemyUserDatabase(session=session, user_table=User, oauth_account_table=OAuthAccount)


UserDatabaseDep = Annotated[BaseUserDatabase, Depends(get_user_database)]

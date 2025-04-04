from __future__ import annotations

import datetime
import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import (
    select,
    or_,
    and_,
    true,
    ColumnElement,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ..db.base import BaseUserDatabase
from ....models.sqlalchemy import (
    User,
    OAuthAccount,
)


class SQLAlchemyUserDatabase(BaseUserDatabase):
    session: AsyncSession
    user_table: type[User]
    oauth_account_table: type[OAuthAccount]

    def __init__(self,
                 *,
                 session: AsyncSession,
                 user_table: type[User],
                 oauth_account_table: type[OAuthAccount]) -> None:
        self.session = session
        self.user_table = user_table
        self.oauth_account_table = oauth_account_table

    async def get(self, id: uuid.UUID) -> User | None:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_list(self,
                       *,
                       id: uuid.UUID | None = None,
                       created: datetime.datetime | None = None,
                       count: int) -> Sequence[User]:
        created_parts: list[ColumnElement[bool]] = []

        if created is not None:
            created_parts.append(
                self.user_table.created > created,
            )

        if created is not None and id is not None:
            created_parts.append(
                and_(
                    self.user_table.created == created,
                    self.user_table.id > id,
                ),
            )

        statement = select(
            self.user_table,
        ).where(
            or_(*created_parts) if created_parts else true(),
        ).limit(
            count,
        ).order_by(
            self.user_table.created,
            self.user_table.id,
        )

        return await self._get_users_list(statement)

    async def get_by_login(self, login: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.login == login)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.email == email)
        return await self._get_user(statement)

    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User | None:
        statement = (
            select(self.user_table)
            .join(self.oauth_account_table)
            .where(self.oauth_account_table.oauth_name == oauth_name)
            .where(self.oauth_account_table.account_id == account_id)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: dict[str, Any]) -> User:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_dict: dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def add_oauth_account(self, user: User, create_dict: dict[str, Any]) -> User:
        await self.session.refresh(user)

        oauth_account = self.oauth_account_table(**create_dict)
        self.session.add(oauth_account)
        user.oauth_accounts.append(oauth_account)
        self.session.add(user)

        await self.session.commit()

        return user

    async def update_oauth_account(self,
                                   user: User,
                                   oauth_account: OAuthAccount,
                                   update_dict: dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(oauth_account, key, value)

        self.session.add(oauth_account)
        await self.session.commit()

        return user

    async def _get_user(self, statement: Select) -> User | None:
        result = await self.session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def _get_users_list(self, statement: Select) -> Sequence[User]:
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

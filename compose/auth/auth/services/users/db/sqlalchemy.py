from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import (
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from .base import BaseUserDatabase
from ...pagination import (
    AbstractPaginationService,
    AbstractPaginator,
    PageParams,
)
from ....models.sqlalchemy import (
    User,
    OAuthAccount,
)


class SQLAlchemyUserDatabase(BaseUserDatabase):
    session: AsyncSession
    user_table: type[User]
    oauth_account_table: type[OAuthAccount]
    pagination_service: AbstractPaginationService

    def __init__(self,
                 *,
                 session: AsyncSession,
                 user_table: type[User],
                 oauth_account_table: type[OAuthAccount],
                 pagination_service: AbstractPaginationService) -> None:
        self.session = session
        self.user_table = user_table
        self.oauth_account_table = oauth_account_table
        self.pagination_service = pagination_service

    async def get(self, id: uuid.UUID) -> User | None:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_list(self, *, page_params: PageParams) -> Sequence[User]:
        statement = select(self.user_table)

        paginator: AbstractPaginator[tuple[User]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=self.user_table.id,
            timestamp_column=self.user_table.created,
        )
        page_statement = paginator.get_page(page_params=page_params)

        return await self._get_users_list(page_statement)

    async def get_by_login(self, login: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.login == login)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(self.user_table).where(self.user_table.email == email)
        return await self._get_user(statement)

    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User | None:
        statement = select(
            self.user_table,
        ).join(
            self.oauth_account_table,
        ).where(
            self.oauth_account_table.oauth_name == oauth_name,
            self.oauth_account_table.account_id == account_id,
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
        oauth_account_data = {
            **create_dict,
            'user_id': user.id,
        }
        oauth_account = self.oauth_account_table(**oauth_account_data)
        self.session.add(oauth_account)

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

    async def _get_user(self, statement: Select[tuple[User]]) -> User | None:
        result = await self.session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def _get_users_list(self, statement: Select[tuple[User]]) -> Sequence[User]:
        result = await self.session.execute(statement)
        return result.unique().scalars().all()

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import (
    select,
    insert,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .base import AbstractUserDatabase
from ...pagination import (
    AbstractPaginationService,
    AbstractPaginator,
    PageParams,
)
from ....models.sqlalchemy import (
    User,
    OAuthAccount,
)


class UserDatabase(AbstractUserDatabase):
    session: AsyncSession
    pagination_service: AbstractPaginationService

    def __init__(self,
                 *,
                 session: AsyncSession,
                 pagination_service: AbstractPaginationService) -> None:
        self.session = session
        self.pagination_service = pagination_service

    async def get(self, *, user_id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == user_id)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_login(self, *, login: str) -> User | None:
        statement = select(User).where(User.login == login)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_email(self, *, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_list(self, *, page_params: PageParams) -> Sequence[User]:
        statement = select(User)

        paginator: AbstractPaginator[tuple[User]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=User.id,
            timestamp_column=User.created,
        )
        page_statement = paginator.get_page(page_params=page_params)

        result = await self.session.execute(page_statement)

        return result.scalars().all()

    async def create(self, *, create_dict: dict[str, Any]) -> User:
        statement = insert(User).values(create_dict).returning(User)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()

    async def update(self, *, user_id: uuid.UUID, update_dict: dict[str, Any]) -> User | None:
        statement = update(User).where(
            User.id == user_id,
        ).values(update_dict).returning(
            User.id,
        )

        result = await self.session.execute(statement)
        await self.session.commit()

        update_user_row = result.one_or_none()

        if update_user_row is None:
            return None

        return await self.get(user_id=update_user_row.id)

    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User | None:
        statement = select(
            User,
        ).join(
            OAuthAccount,
        ).where(
            OAuthAccount.oauth_name == oauth_name,
            OAuthAccount.account_id == account_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def add_oauth_account(self,
                                *,
                                user_id: uuid.UUID,
                                create_dict: dict[str, Any]) -> None:
        create_dict = {
            **create_dict,
            'user_id': user_id,
        }
        statement = insert(OAuthAccount).values(create_dict)

        await self.session.execute(statement)
        await self.session.commit()

    async def update_oauth_account(self,
                                   *,
                                   user_id: uuid.UUID,
                                   oauth_account: OAuthAccount,
                                   update_dict: dict[str, Any]) -> None:
        statement = update(User).where(User.id == user_id).values(update_dict)

        await self.session.execute(statement)
        await self.session.commit()

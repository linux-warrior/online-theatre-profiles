from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
)

from .models import (
    LoginHistoryCreate,
)
from ...pagination import (
    AbstractPaginationService,
    PaginationServiceDep,
    AbstractPaginator,
    PageParams,
)
from ....db.sqlalchemy import (
    AsyncSession,
    AsyncSessionDep,
)
from ....models.sqlalchemy import LoginHistory


class LoginHistoryRepository:
    session: AsyncSession
    pagination_service: AbstractPaginationService

    def __init__(self,
                 *,
                 session: AsyncSession,
                 pagination_service: AbstractPaginationService) -> None:
        self.session = session
        self.pagination_service = pagination_service

    async def get_list(self,
                       *,
                       user_id: uuid.UUID,
                       page_params: PageParams) -> Sequence[LoginHistory]:
        statement = select(LoginHistory).where(LoginHistory.user_id == user_id)

        paginator: AbstractPaginator[tuple[LoginHistory]] = self.pagination_service.get_paginator(
            statement=statement,
            id_column=LoginHistory.id,
            timestamp_column=LoginHistory.created,
        )
        page_statement = paginator.get_page(page_params=page_params)

        result = await self.session.execute(page_statement)

        return result.scalars().all()

    async def create(
            self,
            *,
            user_id: uuid.UUID,
            login_history_create: LoginHistoryCreate) -> LoginHistory:
        login_history_create_dict = {
            **login_history_create.model_dump(),
            'user_id': user_id,
        }
        statement = insert(LoginHistory).values(login_history_create_dict).returning(LoginHistory)

        result = await self.session.execute(statement)
        await self.session.commit()

        return result.scalar_one()


async def get_login_history_repository(session: AsyncSessionDep,
                                       pagination_service: PaginationServiceDep) -> LoginHistoryRepository:
    return LoginHistoryRepository(session=session, pagination_service=pagination_service)


LoginHistoryRepositoryDep = Annotated[LoginHistoryRepository, Depends(get_login_history_repository)]

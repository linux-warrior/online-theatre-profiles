from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from .dependencies import Page
from .models import LoginHistoryCreate
from .repository import (
    LoginHistoryRepositoryDep,
    LoginHistoryRepository
)
from .....models.sqlalchemy import LoginHistory


class LoginHistoryService:
    _repository: LoginHistoryRepository

    def __init__(self, repository: LoginHistoryRepository):
        self._repository = repository

    async def record_to_log(self, row: LoginHistoryCreate):
        await self._repository.create(row)

    async def get_list(self, user_id: uuid.UUID, page: Page) -> Sequence[LoginHistory]:
        return await self._repository.get_list_by_user(user_id, page)


async def get_login_history_service(
        db: LoginHistoryRepositoryDep
) -> LoginHistoryService:
    return LoginHistoryService(db)


LoginHistoryServiceDep = Annotated[
    LoginHistoryService,
    Depends(get_login_history_service)
]

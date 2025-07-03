from __future__ import annotations

import abc
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    LoginHistoryCreateError,
)
from .models import (
    ReadLoginHistoryResponse,
    LoginHistoryCreate,
)
from .repository import (
    LoginHistoryRepository,
    LoginHistoryRepositoryDep,
)
from ...pagination import (
    PageParams,
)
from ....models.schemas import (
    LoginHistorySchema,
)
from ....models.sqlalchemy import (
    LoginHistory,
)


class AbstractLoginHistoryService(abc.ABC):
    @abc.abstractmethod
    async def get_list(self,
                       *,
                       user_id: uuid.UUID,
                       page_params: PageParams) -> list[ReadLoginHistoryResponse]: ...

    @abc.abstractmethod
    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     login_history_create: LoginHistoryCreate) -> ReadLoginHistoryResponse: ...


class LoginHistoryService(AbstractLoginHistoryService):
    repository: LoginHistoryRepository

    def __init__(self, *, repository: LoginHistoryRepository) -> None:
        self.repository = repository

    async def get_list(self,
                       *,
                       user_id: uuid.UUID,
                       page_params: PageParams) -> list[ReadLoginHistoryResponse]:
        login_history_list = await self.repository.get_list(
            user_id=user_id,
            page_params=page_params,
        )

        return [
            self._get_read_login_history_response(login_history=login_history)
            for login_history in login_history_list
        ]

    async def create(self,
                     *,
                     user_id: uuid.UUID,
                     login_history_create: LoginHistoryCreate) -> ReadLoginHistoryResponse:
        try:
            login_history = await self.repository.create(
                user_id=user_id,
                login_history_create=login_history_create,
            )

        except IntegrityError as e:
            raise LoginHistoryCreateError from e

        return self._get_read_login_history_response(login_history=login_history)

    def _get_read_login_history_response(self, *, login_history: LoginHistory) -> ReadLoginHistoryResponse:
        login_history_schema = LoginHistorySchema.model_validate(login_history, from_attributes=True)
        read_user_role_response_dict = login_history_schema.model_dump()

        return ReadLoginHistoryResponse.model_validate(read_user_role_response_dict)


async def get_login_history_service(repository: LoginHistoryRepositoryDep) -> AbstractLoginHistoryService:
    return LoginHistoryService(repository=repository)


LoginHistoryServiceDep = Annotated[AbstractLoginHistoryService, Depends(get_login_history_service)]

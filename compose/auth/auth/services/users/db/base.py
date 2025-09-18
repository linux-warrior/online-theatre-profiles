from __future__ import annotations

import abc
import uuid
from collections.abc import Sequence
from typing import Any

from ...pagination import (
    PageParams,
)
from ....models.sqlalchemy import (
    User,
    OAuthAccount,
)


class AbstractUserDatabase(abc.ABC):
    @abc.abstractmethod
    async def get(self, *, user_id: uuid.UUID) -> User | None: ...

    @abc.abstractmethod
    async def get_by_login(self, *, login: str) -> User | None: ...

    @abc.abstractmethod
    async def get_by_email(self, *, email: str) -> User | None: ...

    @abc.abstractmethod
    async def get_list(self, *, page_params: PageParams) -> Sequence[User]: ...

    @abc.abstractmethod
    async def create(self, *, create_dict: dict[str, Any]) -> User: ...

    @abc.abstractmethod
    async def update(self, *, user_id: uuid.UUID, update_dict: dict[str, Any]) -> User | None: ...

    @abc.abstractmethod
    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User | None: ...

    @abc.abstractmethod
    async def add_oauth_account(self,
                                *,
                                user_id: uuid.UUID,
                                create_dict: dict[str, Any]) -> None: ...

    @abc.abstractmethod
    async def update_oauth_account(self,
                                   *,
                                   user_id: uuid.UUID,
                                   oauth_account: OAuthAccount,
                                   update_dict: dict[str, Any]) -> None: ...

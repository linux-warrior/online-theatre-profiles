from __future__ import annotations

import datetime
import uuid
from collections.abc import Sequence
from typing import Any

from ....models.sqlalchemy import (
    User,
    OAuthAccount,
)


class BaseUserDatabase:
    async def get(self, id: uuid.UUID) -> User | None:
        raise NotImplementedError

    async def get_list(self,
                       *,
                       id: uuid.UUID | None = None,
                       created: datetime.datetime | None = None,
                       count: int) -> Sequence[User]:
        raise NotImplementedError

    async def get_by_login(self, login: str) -> User | None:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    async def get_by_oauth_account(self, *, oauth_name: str, account_id: str) -> User | None:
        raise NotImplementedError

    async def create(self, create_dict: dict[str, Any]) -> User:
        raise NotImplementedError

    async def update(self, user: User, update_dict: dict[str, Any]) -> User:
        raise NotImplementedError

    async def delete(self, user: User) -> None:
        raise NotImplementedError

    async def add_oauth_account(self, user: User, create_dict: dict[str, Any]) -> User:
        raise NotImplementedError

    async def update_oauth_account(self,
                                   user: User,
                                   oauth_account: OAuthAccount,
                                   update_dict: dict[str, Any]) -> User:
        raise NotImplementedError

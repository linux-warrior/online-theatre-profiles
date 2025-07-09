from __future__ import annotations

import abc
import dataclasses
import uuid

from ....manager import UserManager
from ......models.sqlalchemy import User


@dataclasses.dataclass(kw_only=True)
class Token:
    token_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    token: str


class AbstractTokenStrategy(abc.ABC):
    @abc.abstractmethod
    async def read_token(self, *, token: str, user_manager: UserManager) -> User | None: ...

    @abc.abstractmethod
    async def write_token(self, *, user: User, parent_id: uuid.UUID | None = None) -> Token: ...

    @abc.abstractmethod
    async def destroy_token(self, *, token: str, user: User) -> Token | None: ...

    @abc.abstractmethod
    async def destroy_token_id(self, *, token_id: uuid.UUID) -> None: ...

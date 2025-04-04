from __future__ import annotations

import dataclasses
import uuid
from typing import Protocol

from ....manager import UserManager
from ......models.sqlalchemy import User


@dataclasses.dataclass(kw_only=True)
class Token:
    token_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    token: str


class Strategy(Protocol):
    async def read_token(self, token: str, user_manager: UserManager) -> User | None: ...

    async def write_token(self, user: User, parent_id: uuid.UUID | None = None) -> Token: ...

    async def destroy_token(self, token: str, user: User) -> Token | None: ...

    async def destroy_token_id(self, token_id: uuid.UUID) -> None: ...

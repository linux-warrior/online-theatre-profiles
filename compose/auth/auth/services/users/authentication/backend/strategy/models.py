from __future__ import annotations

import dataclasses
import uuid

from pydantic import BaseModel


@dataclasses.dataclass(kw_only=True)
class Token:
    token_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    token: str


class TokenData(BaseModel):
    token_id: uuid.UUID
    user_id: uuid.UUID
    parent_id: uuid.UUID | None = None

from __future__ import annotations

import uuid

from pydantic import BaseModel


class User(BaseModel):
    id: uuid.UUID
    login: str | None = None
    email: str | None = None
    is_superuser: bool = False

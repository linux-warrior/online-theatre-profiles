from __future__ import annotations

import uuid

from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: uuid.UUID
    login: str | None
    email: str | None
    is_superuser: bool
    permissions: list[str]

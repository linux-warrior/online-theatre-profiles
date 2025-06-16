from __future__ import annotations

import uuid

from pydantic import (
    BaseModel,
    EmailStr,
)


class CurrentUser(BaseModel):
    id: uuid.UUID
    login: str | None
    email: EmailStr | None
    is_superuser: bool
    permissions: list[str]

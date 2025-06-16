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

    @property
    def is_admin(self) -> bool:
        return self.is_superuser or 'profiles.admin' in self.permissions

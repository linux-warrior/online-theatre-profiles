from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class UserRead(BaseModel):
    id: uuid.UUID
    login: str | None = None
    email: str | None = None
    is_superuser: bool = False


class UserCreate(BaseModel):
    login: str
    password: str


class UserUpdate(BaseModel):
    login: str | None = None
    password: str | None = None


class ExtendedUserRead(UserRead):
    created: datetime.datetime
    modified: datetime.datetime

from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class CurrentUserResponse(BaseModel):
    id: uuid.UUID
    login: str | None
    email: str | None
    is_superuser: bool


class ReadUserResponse(BaseModel):
    id: uuid.UUID
    login: str | None
    email: str | None
    is_superuser: bool
    created: datetime.datetime
    modified: datetime.datetime


class UserCreate(BaseModel):
    login: str
    password: str


class UserUpdate(BaseModel):
    login: str | None = None
    password: str | None = None

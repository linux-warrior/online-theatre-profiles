from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
)

UserLoginField = Annotated[str, Field(min_length=1, max_length=255)]
UserPasswordField = Annotated[str, Field(min_length=1, max_length=255)]


class CurrentUserResponse(BaseModel):
    id: uuid.UUID
    login: str | None
    email: EmailStr | None
    is_superuser: bool


class ReadUserResponse(BaseModel):
    id: uuid.UUID
    login: str | None
    email: EmailStr | None
    is_superuser: bool
    created: datetime.datetime
    modified: datetime.datetime


class UserCreate(BaseModel):
    login: UserLoginField
    password: UserPasswordField


class UserUpdate(BaseModel):
    login: UserLoginField = ''
    password: UserPasswordField = ''


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str

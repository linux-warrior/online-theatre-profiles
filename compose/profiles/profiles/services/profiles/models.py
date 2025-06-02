from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

PhoneNumberField = Annotated[str, Field(pattern=r'^\+79\d{9}$')]


class ReadProfileResponse(BaseModel):
    user_id: uuid.UUID
    last_name: str
    first_name: str
    patronymic: str
    phone_number: PhoneNumberField | None
    created: datetime.datetime
    modified: datetime.datetime


class ProfileCreate(BaseModel):
    last_name: str = ''
    first_name: str = ''
    patronymic: str = ''
    phone_number: PhoneNumberField | None = None


class ProfileUpdate(BaseModel):
    last_name: str = ''
    first_name: str = ''
    patronymic: str = ''
    phone_number: PhoneNumberField | None = None


class DeleteProfileResponse(BaseModel):
    user_id: uuid.UUID

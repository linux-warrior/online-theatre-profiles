from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel

from ..common import PhoneNumberField


class ReadProfileResponse(BaseModel):
    id: uuid.UUID
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
    id: uuid.UUID
    user_id: uuid.UUID

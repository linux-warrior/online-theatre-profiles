from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

from ..common import PhoneNumberField

LastNameField = Annotated[str, Field(min_length=1, max_length=256)]
FirstNameField = Annotated[str, Field(min_length=1, max_length=256)]
PatronymicField = Annotated[str, Field(max_length=256)]


class ReadProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    last_name: LastNameField
    first_name: FirstNameField
    patronymic: PatronymicField
    phone_number: PhoneNumberField | None
    created: datetime.datetime
    modified: datetime.datetime


class ProfileCreate(BaseModel):
    last_name: LastNameField
    first_name: FirstNameField
    patronymic: PatronymicField
    phone_number: PhoneNumberField | None = None


class ProfileUpdate(BaseModel):
    last_name: LastNameField = ''
    first_name: FirstNameField = ''
    patronymic: PatronymicField = ''
    phone_number: PhoneNumberField | None = None


class DeleteProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

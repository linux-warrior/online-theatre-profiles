from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

PermissionNameField = Annotated[str, Field(min_length=1, max_length=255)]
PermissionCodeField = Annotated[str, Field(min_length=1, max_length=255)]


class ReadPermissionResponse(BaseModel):
    id: uuid.UUID
    name: PermissionNameField
    code: PermissionCodeField
    created: datetime.datetime
    modified: datetime.datetime


class PermissionCreate(BaseModel):
    name: PermissionNameField
    code: PermissionCodeField


class PermissionUpdate(BaseModel):
    name: PermissionNameField = ''
    code: PermissionCodeField = ''


class DeletePermissionResponse(BaseModel):
    id: uuid.UUID

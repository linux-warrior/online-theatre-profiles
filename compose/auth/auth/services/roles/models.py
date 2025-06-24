from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

RoleNameField = Annotated[str, Field(min_length=1, max_length=255)]


class ReadRoleResponse(BaseModel):
    id: uuid.UUID
    name: RoleNameField
    created: datetime.datetime
    modified: datetime.datetime


class RoleCreate(BaseModel):
    name: RoleNameField


class RoleUpdate(BaseModel):
    name: RoleNameField = ''


class DeleteRoleResponse(BaseModel):
    id: uuid.UUID

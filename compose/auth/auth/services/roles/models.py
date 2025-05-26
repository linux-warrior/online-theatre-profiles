from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class ReadRoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    created: datetime.datetime
    modified: datetime.datetime


class RoleCreate(BaseModel):
    name: str


class RoleUpdate(BaseModel):
    name: str | None = None


class DeleteRoleResponse(BaseModel):
    id: uuid.UUID

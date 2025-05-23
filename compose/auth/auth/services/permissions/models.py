from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class ReadPermissionResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    created: datetime.datetime
    modified: datetime.datetime


class PermissionCreate(BaseModel):
    name: str
    code: str


class PermissionUpdate(BaseModel):
    name: str | None = None
    code: str | None = None


class DeletePermissionResponse(BaseModel):
    id: uuid.UUID

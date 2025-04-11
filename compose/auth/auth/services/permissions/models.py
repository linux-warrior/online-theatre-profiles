from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class CreatePermissionDto(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID


class PermissionInDb(BaseModel):
    id: uuid.UUID
    role_id: uuid.UUID
    created: datetime


class DeletePermission(BaseModel):
    id: uuid.UUID
    role_id: uuid.UUID

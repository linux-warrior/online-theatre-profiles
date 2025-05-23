from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class RolePermissionRead(BaseModel):
    id: uuid.UUID
    role_id: uuid.UUID
    permission_id: uuid.UUID
    created: datetime.datetime


class RolePermissionDelete(BaseModel):
    id: uuid.UUID

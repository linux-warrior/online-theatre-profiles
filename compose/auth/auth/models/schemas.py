from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class RoleSchema(BaseModel):
    id: uuid.UUID
    name: str
    created: datetime.datetime
    modified: datetime.datetime


class UserRoleSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    created: datetime.datetime


class PermissionSchema(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    created: datetime.datetime
    modified: datetime.datetime


class RolePermissionSchema(BaseModel):
    id: uuid.UUID
    role_id: uuid.UUID
    permission_id: uuid.UUID
    created: datetime.datetime

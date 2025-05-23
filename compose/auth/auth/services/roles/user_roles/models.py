from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class ReadUserRoleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    created: datetime.datetime


class DeleteUserRoleResponse(BaseModel):
    id: uuid.UUID

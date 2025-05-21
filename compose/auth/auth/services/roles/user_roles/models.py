from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class UserRoleRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    created: datetime.datetime


class UserRoleDelete(BaseModel):
    id: uuid.UUID

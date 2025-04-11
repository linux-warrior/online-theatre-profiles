from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CodeRole(str, Enum):
    ADMINISTRATOR = 'admin'
    SUBSCRIBERS = 'subscribers'
    USERS = 'users'


class RoleCreateDto(BaseModel):
    name: str
    code: CodeRole


class RoleUpdateDto(BaseModel):
    name: Optional[str] = None
    code: Optional[CodeRole] = None


class RoleInDB(BaseModel):
    id: uuid.UUID
    name: str
    code: CodeRole
    created: datetime
    modified: datetime


class RoleDelete(BaseModel):
    id: uuid.UUID

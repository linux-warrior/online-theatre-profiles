from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class LoginHistoryCreate(BaseModel):
    user_id: uuid.UUID
    user_agent: str


class LoginHistoryInDb(BaseModel):
    id: uuid.UUID
    user_agent: str
    created: datetime

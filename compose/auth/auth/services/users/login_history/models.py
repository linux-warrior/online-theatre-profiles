from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

UserAgentField = Annotated[str, Field(max_length=65535)]


class ReadLoginHistoryResponse(BaseModel):
    id: uuid.UUID
    user_agent: UserAgentField
    created: datetime.datetime


class LoginHistoryCreate(BaseModel):
    user_agent: UserAgentField

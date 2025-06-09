from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from fastapi import Depends
from pydantic import (
    BaseModel,
    Field,
)


class PageParams(BaseModel):
    id: uuid.UUID | None = Field(default=None, alias='page_id')
    timestamp: datetime.datetime | None = Field(default=None, alias='page_timestamp')
    size: int | None = Field(default=None, ge=1, le=100, alias='page_size')


PageParamsDep = Annotated[PageParams, Depends()]

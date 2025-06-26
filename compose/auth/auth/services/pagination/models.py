from __future__ import annotations

import datetime
import enum
import uuid
from typing import Annotated

from fastapi import Depends
from pydantic import (
    BaseModel,
    Field,
)


class SortOrder(enum.StrEnum):
    ASC = 'asc'
    DESC = 'desc'


class PageParams(BaseModel):
    id: uuid.UUID | None = Field(default=None, alias='page_id')
    timestamp: datetime.datetime | None = Field(default=None, alias='page_timestamp')
    size: int | None = Field(default=None, ge=1, le=100, alias='page_size')
    sort_order: SortOrder = SortOrder.ASC


PageParamsDep = Annotated[PageParams, Depends()]

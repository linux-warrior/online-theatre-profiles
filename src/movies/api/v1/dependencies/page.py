from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from pydantic import (
    BaseModel,
    Field,
)


class PageParams(BaseModel):
    size: int = Field(default=50, ge=1, le=50, alias='page_size')
    number: int = Field(default=1, ge=1, alias='page_number')


PageParamsDep = Annotated[PageParams, Depends()]

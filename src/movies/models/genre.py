from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class Genre(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')
    name: str

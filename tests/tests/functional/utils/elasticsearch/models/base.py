from __future__ import annotations

import uuid

from pydantic import (
    BaseModel,
    Field,
)


class Document(BaseModel):
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4())


class DocumentRelation(BaseModel):
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4())

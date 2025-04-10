from __future__ import annotations

import uuid

from pydantic import (
    BaseModel,
    Field,
)


class Document(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')


class DocumentRelation(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')

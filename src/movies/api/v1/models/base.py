from __future__ import annotations

import uuid

from pydantic import (
    BaseModel,
    Field,
)


class DocumentResponse(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')


class DocumentRelationResponse(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')

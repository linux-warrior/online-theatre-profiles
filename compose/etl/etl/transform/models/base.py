from __future__ import annotations

import uuid

from pydantic import BaseModel


class Document(BaseModel):
    id: uuid.UUID


class DocumentRelation(BaseModel):
    id: uuid.UUID

from __future__ import annotations

import uuid

from pydantic import BaseModel


class Genre(BaseModel):
    uuid: uuid.UUID
    name: str

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class Person(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')
    full_name: str
    films: list[PersonFilmRoles]

class PersonFilmRoles(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')
    roles: list[str]

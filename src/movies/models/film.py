from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class PersonMixin:
    id: uuid.UUID = Field(serialization_alias='uuid')
    full_name: str


class Director(BaseModel, PersonMixin):
    pass


class Actor(BaseModel, PersonMixin):
    pass


class Writer(BaseModel, PersonMixin):
    pass


class Genre(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')
    name: str


class Film(BaseModel):
    id: uuid.UUID = Field(serialization_alias='uuid')
    title: str
    description: str | None
    rating: float | None = Field(serialization_alias='imdb_rating')
    genres: list[Genre] = Field(serialization_alias='genre')
    directors: list[Director] | None
    actors: list[Actor] | None
    writers: list[Writer] | None

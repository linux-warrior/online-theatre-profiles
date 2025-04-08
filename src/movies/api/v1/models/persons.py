from __future__ import annotations

import uuid

from pydantic import BaseModel


class PersonFilmRoles(BaseModel):
    uuid: uuid.UUID
    roles: list[str]


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    films: list[PersonFilmRoles]


class PersonFilm(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float

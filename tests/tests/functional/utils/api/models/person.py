from __future__ import annotations

from .base import (
    Document,
    DocumentRelation,
)

from pydantic import Field


class Person(Document):
    full_name: str
    films: list[PersonFilmRelation]


class PersonFilmRelation(DocumentRelation):
    roles: list[str]


class PersonFilm(Document):
    title: str
    rating: float | None = Field(serialization_alias='imdb_rating')

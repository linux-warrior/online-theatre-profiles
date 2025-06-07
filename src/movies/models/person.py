from __future__ import annotations

from .base import (
    Document,
    DocumentRelation,
)


class Person(Document):
    full_name: str
    films: list[PersonFilm]


class PersonFilm(DocumentRelation):
    roles: list[str]

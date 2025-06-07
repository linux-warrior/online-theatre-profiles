from __future__ import annotations

from .base import (
    DocumentResponse,
    DocumentRelationResponse,
)


class PersonResponse(DocumentResponse):
    full_name: str
    films: list[PersonFilmResponse]


class PersonFilmResponse(DocumentRelationResponse):
    roles: list[str]

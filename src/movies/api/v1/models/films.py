from __future__ import annotations

from pydantic import Field

from .base import (
    DocumentResponse,
    DocumentRelationResponse,
)


class FilmResponse(DocumentResponse):
    title: str
    rating: float | None = Field(serialization_alias='imdb_rating')


class ExtendedFilmResponse(FilmResponse):
    description: str | None
    genres: list[FilmGenreResponse] = Field(serialization_alias='genre')
    directors: list[FilmDirectorResponse]
    actors: list[FilmActorResponse]
    writers: list[FilmWriterResponse]


class FilmGenreResponse(DocumentRelationResponse):
    name: str


class FilmPersonResponse(DocumentRelationResponse):
    full_name: str


class FilmDirectorResponse(FilmPersonResponse):
    pass


class FilmActorResponse(FilmPersonResponse):
    pass


class FilmWriterResponse(FilmPersonResponse):
    pass

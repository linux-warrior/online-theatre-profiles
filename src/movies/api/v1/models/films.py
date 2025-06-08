from __future__ import annotations

import decimal
import uuid

from pydantic import (
    BaseModel,
    Field,
)

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
    users: FilmUsersResponse = Field(default_factory=lambda: FilmUsersResponse())


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


class FilmUsersResponse(BaseModel):
    rating: FilmRatingResponse | None = None
    reviews: FilmReviewsResponse | None = None


class FilmRatingResponse(BaseModel):
    rating: decimal.Decimal | None


class FilmReviewsResponse(BaseModel):
    reviews: list[ReviewResponse]
    rating: decimal.Decimal | None


class ReviewResponse(BaseModel):
    id: uuid.UUID
    summary: str
    content: str
    rating: decimal.Decimal | None

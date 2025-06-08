from __future__ import annotations

import datetime
import decimal
import uuid

from pydantic import BaseModel


class FilmRating(BaseModel):
    rating: decimal.Decimal | None


class FilmReviews(BaseModel):
    reviews: list[Review]
    rating: decimal.Decimal | None


class Review(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    film_id: uuid.UUID
    summary: str
    content: str
    rating: decimal.Decimal | None
    created: datetime.datetime
    modified: datetime.datetime

from __future__ import annotations

import datetime
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

from ..common import RatingField

SummaryField = Annotated[str, Field(min_length=1, max_length=256)]
ContentField = Annotated[str, Field(min_length=1, max_length=65536)]


class ReadReviewResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    film_id: uuid.UUID
    summary: SummaryField
    content: ContentField
    rating: RatingField | None
    created: datetime.datetime
    modified: datetime.datetime


class ReviewCreate(BaseModel):
    summary: SummaryField
    content: ContentField
    rating: RatingField | None = None


class ReviewUpdate(BaseModel):
    summary: SummaryField = ''
    content: ContentField = ''
    rating: RatingField | None = None


class DeleteReviewResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID


class FilmReviewsResponse(BaseModel):
    reviews: list[ReadReviewResponse]
    rating: RatingField | None

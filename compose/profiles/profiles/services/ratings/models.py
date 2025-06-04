from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

RatingField = Annotated[Decimal, Field(max_digits=3, decimal_places=1, ge=0, le=10)]


class ReadRatingResponse(BaseModel):
    user_id: uuid.UUID
    film_id: uuid.UUID
    rating: RatingField
    created: datetime.datetime
    modified: datetime.datetime


class RatingCreate(BaseModel):
    rating: RatingField


class RatingUpdate(BaseModel):
    rating: RatingField


class DeleteRatingResponse(BaseModel):
    user_id: uuid.UUID
    film_id: uuid.UUID

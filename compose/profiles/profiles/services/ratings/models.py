from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel

from ..common import RatingField


class ReadRatingResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    film_id: uuid.UUID
    rating: RatingField
    created: datetime.datetime
    modified: datetime.datetime


class RatingCreate(BaseModel):
    rating: RatingField


class RatingUpdate(BaseModel):
    rating: RatingField


class DeleteRatingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID

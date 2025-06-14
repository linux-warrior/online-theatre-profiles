from __future__ import annotations

import datetime
import decimal
import uuid

from pydantic import BaseModel


class ProfileSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    last_name: str
    first_name: str
    patronymic: str
    phone_number: str | None
    phone_number_hash: str | None
    created: datetime.datetime
    modified: datetime.datetime


class FavoriteSchema(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    film_id: uuid.UUID
    created: datetime.datetime


class RatingSchema(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    film_id: uuid.UUID
    rating: decimal.Decimal
    created: datetime.datetime
    modified: datetime.datetime


class ReviewSchema(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    film_id: uuid.UUID
    summary: str
    content: str
    rating: decimal.Decimal | None
    created: datetime.datetime
    modified: datetime.datetime

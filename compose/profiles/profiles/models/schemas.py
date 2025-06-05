from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel


class ProfileSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    last_name: str
    first_name: str
    patronymic: str
    phone_number: str | None
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
    rating: Decimal
    created: datetime.datetime
    modified: datetime.datetime

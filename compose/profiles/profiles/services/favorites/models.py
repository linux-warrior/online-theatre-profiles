from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class ReadFavoriteResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    film_id: uuid.UUID
    created: datetime.datetime


class DeleteFavoriteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    film_id: uuid.UUID

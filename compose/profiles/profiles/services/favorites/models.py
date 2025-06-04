from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel


class ReadFavoriteResponse(BaseModel):
    user_id: uuid.UUID
    film_id: uuid.UUID
    created: datetime.datetime


class DeleteFavoriteResponse(BaseModel):
    user_id: uuid.UUID
    film_id: uuid.UUID

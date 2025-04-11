from __future__ import annotations

import datetime
import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class StateModel(BaseModel):
    model_config = ConfigDict(strict=True)


class State(StateModel):
    extractors: ExtractorsState = Field(default_factory=lambda: ExtractorsState())


class ExtractorsState(StateModel):
    film_works: ExtractorState = Field(default_factory=lambda: ExtractorState())
    genres: ExtractorState = Field(default_factory=lambda: ExtractorState())
    persons: ExtractorState = Field(default_factory=lambda: ExtractorState())


class ExtractorState(StateModel):
    last_modified: LastModified = Field(default_factory=lambda: LastModified())


class LastModified(StateModel):
    model_config = ConfigDict(frozen=True)

    modified: datetime.datetime | None = Field(default=None)
    id: uuid.UUID | None = Field(default=None)

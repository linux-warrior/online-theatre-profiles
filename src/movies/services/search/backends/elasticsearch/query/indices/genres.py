from __future__ import annotations

import abc
import uuid

from ..query import (
    ElasticsearchGetQuery,
    ElasticsearchSearchQuery,
)
from .......core.config import settings


class GetGenreQuery(ElasticsearchGetQuery):
    genre_id: uuid.UUID

    def __init__(self, *, genre_id: uuid.UUID) -> None:
        self.genre_id = genre_id

    def get_index(self) -> str:
        return settings.elasticsearch.index_name_genres

    def get_id(self) -> str:
        return str(self.genre_id)


class BaseSearchGenresQuery(ElasticsearchSearchQuery, abc.ABC):
    def get_index(self) -> str:
        return settings.elasticsearch.index_name_genres


class GenresListQuery(BaseSearchGenresQuery):
    page_number: int
    page_size: int

    def __init__(self, *, page_number: int, page_size: int) -> None:
        self.page_number = page_number
        self.page_size = page_size

    def get_body(self) -> dict:
        return {
            'size': self.page_size,
            'from': (self.page_number - 1) * self.page_size,
        }

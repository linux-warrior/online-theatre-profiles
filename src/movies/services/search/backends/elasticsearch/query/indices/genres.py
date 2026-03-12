from __future__ import annotations

import abc
import uuid
from typing import TYPE_CHECKING

from ..query import (
    ElasticsearchGetQuery,
    ElasticsearchSearchQuery,
)
from .......core.config import settings

if TYPE_CHECKING:
    from ...backend import ElasticsearchSearchBackend


class GetGenreQuery(ElasticsearchGetQuery):
    _genre_id: uuid.UUID

    def __init__(self, *, backend: ElasticsearchSearchBackend, genre_id: uuid.UUID) -> None:
        super().__init__(backend=backend)
        self._genre_id = genre_id

    def get_index(self) -> str:
        return settings.elasticsearch.index_name_genres

    def get_id(self) -> str:
        return str(self._genre_id)


class BaseSearchGenresQuery(ElasticsearchSearchQuery, abc.ABC):
    def get_index(self) -> str:
        return settings.elasticsearch.index_name_genres


class GenresListQuery(BaseSearchGenresQuery):
    _page_number: int
    _page_size: int

    def __init__(self, *, backend: ElasticsearchSearchBackend, page_number: int, page_size: int) -> None:
        super().__init__(backend=backend)
        self._page_number = page_number
        self._page_size = page_size

    def get_body(self) -> dict:
        return {
            'size': self._page_size,
            'from': (self._page_number - 1) * self._page_size,
        }

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


class GetPersonQuery(ElasticsearchGetQuery):
    _person_id: uuid.UUID

    def __init__(self, *, backend: ElasticsearchSearchBackend, person_id: uuid.UUID) -> None:
        super().__init__(backend=backend)
        self._person_id = person_id

    def get_index(self) -> str:
        return settings.elasticsearch.index_name_persons

    def get_id(self) -> str:
        return str(self._person_id)


class BaseSearchPersonsQuery(ElasticsearchSearchQuery, abc.ABC):
    def get_index(self) -> str:
        return settings.elasticsearch.index_name_persons


class SearchPersonsQuery(BaseSearchPersonsQuery):
    _query: str
    _page_number: int
    _page_size: int

    def __init__(self,
                 *,
                 backend: ElasticsearchSearchBackend,
                 query: str,
                 page_number: int,
                 page_size: int) -> None:
        super().__init__(backend=backend)
        self._query = query
        self._page_number = page_number
        self._page_size = page_size

    def get_body(self) -> dict:
        return {
            'query': {
                'match': {
                    'full_name': self._query,
                },
            },
            'size': self._page_size,
            'from': (self._page_number - 1) * self._page_size,
        }

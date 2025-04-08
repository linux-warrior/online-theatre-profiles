from __future__ import annotations

import abc
import uuid

from ..query import (
    ElasticsearchGetQuery,
    ElasticsearchSearchQuery,
)
from .......core.config import settings


class GetPersonQuery(ElasticsearchGetQuery):
    person_id: uuid.UUID

    def __init__(self, *, person_id: uuid.UUID) -> None:
        self.person_id = person_id

    def get_index(self) -> str:
        return settings.elasticsearch.index_name_persons

    def get_id(self) -> str:
        return str(self.person_id)


class BaseSearchPersonsQuery(ElasticsearchSearchQuery, abc.ABC):
    def get_index(self) -> str:
        return settings.elasticsearch.index_name_persons


class SearchPersonsQuery(BaseSearchPersonsQuery):
    query: str
    page_number: int
    page_size: int

    def __init__(self, *, query: str, page_number: int, page_size: int) -> None:
        self.query = query
        self.page_number = page_number
        self.page_size = page_size

    def get_body(self) -> dict:
        return {
            'query': {
                'match': {
                    'full_name': self.query,
                },
            },
            'size': self.page_size,
            'from': (self.page_number - 1) * self.page_size,
        }

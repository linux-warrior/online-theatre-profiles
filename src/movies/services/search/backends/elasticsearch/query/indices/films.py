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


class GetFilmQuery(ElasticsearchGetQuery):
    _film_id: uuid.UUID

    def __init__(self, *, backend: ElasticsearchSearchBackend, film_id: uuid.UUID) -> None:
        super().__init__(backend=backend)
        self._film_id = film_id

    def get_index(self) -> str:
        return settings.elasticsearch.index_name_films

    def get_id(self) -> str:
        return str(self._film_id)


class BaseSearchFilmsQuery(ElasticsearchSearchQuery, abc.ABC):
    def get_index(self) -> str:
        return settings.elasticsearch.index_name_films


class FilmsByPersonQuery(BaseSearchFilmsQuery):
    _person_id: uuid.UUID

    def __init__(self, *, backend: ElasticsearchSearchBackend, person_id: uuid.UUID) -> None:
        super().__init__(backend=backend)
        self._person_id = person_id

    def get_body(self) -> dict:
        return {
            'query': {
                'bool': {
                    'should': [
                        {
                            'nested': {
                                'path': 'actors',
                                'query': {
                                    'term': {
                                        'actors.id': str(self._person_id),
                                    },
                                },
                            },
                        },
                        {
                            'nested': {
                                'path': 'directors',
                                'query': {
                                    'term': {
                                        'directors.id': str(self._person_id),
                                    },
                                },
                            },
                        },
                        {
                            'nested': {
                                'path': 'writers',
                                'query': {
                                    'term': {
                                        'writers.id': str(self._person_id),
                                    },
                                },
                            },
                        },
                    ],
                    'minimum_should_match': 1,
                },
            },
        }


class FilmsListQuery(BaseSearchFilmsQuery):
    _sort: dict
    _page_number: int
    _page_size: int
    _genre_id: uuid.UUID | None

    def __init__(self,
                 *,
                 backend: ElasticsearchSearchBackend,
                 sort: dict,
                 page_number: int,
                 page_size: int,
                 genre_id: uuid.UUID | None = None) -> None:
        super().__init__(backend=backend)
        self._sort = sort
        self._page_number = page_number
        self._page_size = page_size
        self._genre_id = genre_id

    def get_body(self) -> dict:
        body = {
            'sort': {
                self._sort['field']: {
                    'order': self._sort['order'],
                },
            },
            'size': self._page_size,
            'from': (self._page_number - 1) * self._page_size,
        }

        if self._genre_id is not None:
            body['query'] = {
                'nested': {
                    'path': 'genres',
                    'query': {
                        'term': {
                            'genres.id': str(self._genre_id),
                        },
                    },
                },
            }

        return body


class SearchFilmsQuery(BaseSearchFilmsQuery):
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
                    'title': self._query,
                },
            },
            'size': self._page_size,
            'from': (self._page_number - 1) * self._page_size,
        }

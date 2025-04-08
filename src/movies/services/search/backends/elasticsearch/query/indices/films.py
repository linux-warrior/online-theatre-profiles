from __future__ import annotations

import abc
import uuid

from ..query import (
    ElasticsearchGetQuery,
    ElasticsearchSearchQuery,
)
from .......core.config import settings


class GetFilmQuery(ElasticsearchGetQuery):
    film_id: uuid.UUID

    def __init__(self, *, film_id: uuid.UUID) -> None:
        self.film_id = film_id

    def get_index(self) -> str:
        return settings.elasticsearch.index_name_films

    def get_id(self) -> str:
        return str(self.film_id)


class BaseSearchFilmsQuery(ElasticsearchSearchQuery, abc.ABC):
    def get_index(self) -> str:
        return settings.elasticsearch.index_name_films


class FilmsByPersonQuery(BaseSearchFilmsQuery):
    person_id: uuid.UUID

    def __init__(self, *, person_id: uuid.UUID) -> None:
        self.person_id = person_id

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
                                        'actors.id': str(self.person_id),
                                    },
                                },
                            },
                        },
                        {
                            'nested': {
                                'path': 'directors',
                                'query': {
                                    'term': {
                                        'directors.id': str(self.person_id),
                                    },
                                },
                            },
                        },
                        {
                            'nested': {
                                'path': 'writers',
                                'query': {
                                    'term': {
                                        'writers.id': str(self.person_id),
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
    sort: dict
    page_number: int
    page_size: int
    genre_id: uuid.UUID | None

    def __init__(self,
                 *,
                 sort: dict,
                 page_number: int,
                 page_size: int,
                 genre_id: uuid.UUID | None = None) -> None:
        self.sort = sort
        self.page_number = page_number
        self.page_size = page_size
        self.genre_id = genre_id

    def get_body(self) -> dict:
        body = {
            'sort': {
                self.sort['field']: {
                    'order': self.sort['order'],
                },
            },
            'size': self.page_size,
            'from': (self.page_number - 1) * self.page_size,
        }

        if self.genre_id is not None:
            body['query'] = {
                'nested': {
                    'path': 'genres',
                    'query': {
                        'term': {
                            'genres.id': str(self.genre_id),
                        },
                    },
                },
            }

        return body


class SearchFilmsQuery(BaseSearchFilmsQuery):
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
                    'title': self.query,
                },
            },
            'size': self.page_size,
            'from': (self.page_number - 1) * self.page_size,
        }

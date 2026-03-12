from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from .indices import (
    films,
    genres,
    persons,
)
from .query import (
    ElasticsearchGetQuery,
    ElasticsearchSearchQuery,
)
from ...base import (
    AbstractGetQuery,
    AbstractSearchQuery,
    AbstractQueryFactory,
)

if TYPE_CHECKING:
    from ..backend import ElasticsearchSearchBackend


class ElasticsearchQueryFactory(AbstractQueryFactory):
    _backend: ElasticsearchSearchBackend

    def __init__(self, *, backend: ElasticsearchSearchBackend) -> None:
        self._backend = backend

    def get_film(self, *, film_id: uuid.UUID) -> ElasticsearchGetQuery:
        return films.GetFilmQuery(backend=self._backend, film_id=film_id)

    def films_by_person(self, *, person_id: uuid.UUID) -> ElasticsearchSearchQuery:
        return films.FilmsByPersonQuery(backend=self._backend, person_id=person_id)

    def films_list(self,
                   *,
                   sort: dict,
                   page_number: int,
                   page_size: int,
                   genre_id: uuid.UUID | None = None) -> ElasticsearchSearchQuery:
        return films.FilmsListQuery(
            backend=self._backend,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            genre_id=genre_id,
        )

    def search_films(self, *, query: str, page_number: int, page_size: int) -> AbstractSearchQuery:
        return films.SearchFilmsQuery(
            backend=self._backend,
            query=query,
            page_number=page_number,
            page_size=page_size,
        )

    def get_genre(self, *, genre_id: uuid.UUID) -> AbstractGetQuery:
        return genres.GetGenreQuery(backend=self._backend, genre_id=genre_id)

    def genres_list(self, *, page_number: int, page_size: int) -> AbstractSearchQuery:
        return genres.GenresListQuery(
            backend=self._backend,
            page_number=page_number,
            page_size=page_size,
        )

    def get_person(self, *, person_id: uuid.UUID) -> AbstractGetQuery:
        return persons.GetPersonQuery(backend=self._backend, person_id=person_id)

    def search_persons(self, *, query: str, page_number: int, page_size: int) -> AbstractSearchQuery:
        return persons.SearchPersonsQuery(
            backend=self._backend,
            query=query,
            page_number=page_number,
            page_size=page_size,
        )

from __future__ import annotations

import uuid

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


class ElasticsearchQueryFactory(AbstractQueryFactory):
    def get_film(self, *, film_id: uuid.UUID) -> ElasticsearchGetQuery:
        return films.GetFilmQuery(film_id=film_id)

    def films_by_person(self, *, person_id: uuid.UUID) -> ElasticsearchSearchQuery:
        return films.FilmsByPersonQuery(person_id=person_id)

    def films_list(self,
                   *,
                   sort: dict,
                   page_number: int,
                   page_size: int,
                   genre_id: uuid.UUID | None = None) -> ElasticsearchSearchQuery:
        return films.FilmsListQuery(
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            genre_id=genre_id,
        )

    def search_films(self, *, query: str, page_number: int, page_size: int) -> AbstractSearchQuery:
        return films.SearchFilmsQuery(query=query, page_number=page_number, page_size=page_size)

    def get_genre(self, *, genre_id: uuid.UUID) -> AbstractGetQuery:
        return genres.GetGenreQuery(genre_id=genre_id)

    def genres_list(self, *, page_number: int, page_size: int) -> AbstractSearchQuery:
        return genres.GenresListQuery(page_number=page_number, page_size=page_size)

    def get_person(self, *, person_id: uuid.UUID) -> AbstractGetQuery:
        return persons.GetPersonQuery(person_id=person_id)

    def search_persons(self, *, query: str, page_number: int, page_size: int) -> AbstractSearchQuery:
        return persons.SearchPersonsQuery(query=query, page_number=page_number, page_size=page_size)

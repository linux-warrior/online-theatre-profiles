from __future__ import annotations

import abc
import uuid

from .query import (
    AbstractGetQuery,
    AbstractSearchQuery,
)


class AbstractQueryFactory(abc.ABC):
    @abc.abstractmethod
    def get_film(self, *, film_id: uuid.UUID) -> AbstractGetQuery: ...

    @abc.abstractmethod
    def films_by_person(self, *, person_id: uuid.UUID) -> AbstractSearchQuery: ...

    @abc.abstractmethod
    def films_list(self,
                   *,
                   sort: dict,
                   page_number: int,
                   page_size: int,
                   genre_id: uuid.UUID | None = None) -> AbstractSearchQuery: ...

    @abc.abstractmethod
    def search_films(self, *, query: str, page_number: int, page_size: int) -> AbstractSearchQuery: ...

    @abc.abstractmethod
    def get_genre(self, *, genre_id: uuid.UUID) -> AbstractGetQuery: ...

    @abc.abstractmethod
    def genres_list(self, *, page_number: int, page_size: int) -> AbstractSearchQuery: ...

    @abc.abstractmethod
    def get_person(self, *, person_id: uuid.UUID) -> AbstractGetQuery: ...

    @abc.abstractmethod
    def search_persons(self, *, query: str, page_number: int, page_size: int) -> AbstractSearchQuery: ...

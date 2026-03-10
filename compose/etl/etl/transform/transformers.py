from __future__ import annotations

import dataclasses
import uuid
from collections import defaultdict

from .models import (
    Film,
    FilmGenre,
    FilmDirector,
    FilmActor,
    FilmWriter,
    Genre,
    Person,
    PersonFilm,
)
from ..extract import (
    FilmWorksVisitor,
    GenresVisitor,
    PersonsVisitor,
)
from ..state import LastModified


@dataclasses.dataclass(kw_only=True)
class FilmTransformState:
    genres_names: list[str] = dataclasses.field(default_factory=list)
    directors_names: list[str] = dataclasses.field(default_factory=list)
    actors_names: list[str] = dataclasses.field(default_factory=list)
    writers_names: list[str] = dataclasses.field(default_factory=list)
    genres: list[FilmGenre] = dataclasses.field(default_factory=list)
    directors: list[FilmDirector] = dataclasses.field(default_factory=list)
    actors: list[FilmActor] = dataclasses.field(default_factory=list)
    writers: list[FilmWriter] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(kw_only=True)
class FilmsTransformResult:
    films: list[Film] = dataclasses.field(default_factory=list)
    last_modified: LastModified = dataclasses.field(default_factory=lambda: LastModified())


class FilmsTransformer(FilmWorksVisitor):
    _film_state: FilmTransformState
    _result: FilmsTransformResult

    def __init__(self) -> None:
        self._film_state = FilmTransformState()
        self._result = FilmsTransformResult()

    @property
    def result(self) -> FilmsTransformResult:
        return self._result

    def start_handle_film_work(self, *, film_work_data: dict) -> None:
        self._film_state = FilmTransformState()

    def end_handle_film_work(self, *, film_work_data: dict) -> None:
        self._result.films.append(Film(
            id=film_work_data['id'],
            title=film_work_data['title'],
            description=film_work_data['description'],
            rating=film_work_data['rating'],
            genres_names=self._film_state.genres_names,
            directors_names=self._film_state.directors_names,
            actors_names=self._film_state.actors_names,
            writers_names=self._film_state.writers_names,
            genres=self._film_state.genres,
            directors=self._film_state.directors,
            actors=self._film_state.actors,
            writers=self._film_state.writers,
        ))

        self._result.last_modified = LastModified(
            modified=film_work_data['modified'],
            id=film_work_data['id'],
        )

    def handle_genre(self, *, genre_data: dict) -> None:
        self._film_state.genres_names.append(genre_data['name'])
        self._film_state.genres.append(FilmGenre(
            id=genre_data['id'],
            name=genre_data['name'],
        ))

    def handle_person(self, *, person_data: dict) -> None:
        if person_data['role'] == 'director':
            self._film_state.directors_names.append(person_data['full_name'])
            self._film_state.directors.append(FilmDirector(
                id=person_data['id'],
                full_name=person_data['full_name'],
            ))
            return

        if person_data['role'] == 'actor':
            self._film_state.actors_names.append(person_data['full_name'])
            self._film_state.actors.append(FilmActor(
                id=person_data['id'],
                full_name=person_data['full_name'],
            ))
            return

        if person_data['role'] == 'writer':
            self._film_state.writers_names.append(person_data['full_name'])
            self._film_state.writers.append(FilmWriter(
                id=person_data['id'],
                full_name=person_data['full_name'],
            ))


@dataclasses.dataclass(kw_only=True)
class GenresTransformResult:
    genres: list[Genre] = dataclasses.field(default_factory=list)
    last_modified: LastModified = dataclasses.field(default_factory=lambda: LastModified())


class GenresTransformer(GenresVisitor):
    _result: GenresTransformResult

    def __init__(self) -> None:
        self._result = GenresTransformResult()

    @property
    def result(self) -> GenresTransformResult:
        return self._result

    def handle_genre(self, *, genre_data: dict) -> None:
        self._result.genres.append(Genre(
            id=genre_data['id'],
            name=genre_data['name'],
        ))

        self._result.last_modified = LastModified(
            modified=genre_data['modified'],
            id=genre_data['id'],
        )


@dataclasses.dataclass(kw_only=True)
class PersonTransformState:
    films: dict[uuid.UUID, list[str]] = dataclasses.field(default_factory=lambda: defaultdict(list))


@dataclasses.dataclass(kw_only=True)
class PersonsTransformResult:
    persons: list[Person] = dataclasses.field(default_factory=list)
    last_modified: LastModified = dataclasses.field(default_factory=lambda: LastModified())


class PersonsTransformer(PersonsVisitor):
    _person_state: PersonTransformState
    _result: PersonsTransformResult

    def __init__(self) -> None:
        self._person_state = PersonTransformState()
        self._result = PersonsTransformResult()

    @property
    def result(self) -> PersonsTransformResult:
        return self._result

    def start_handle_person(self, *, person_data: dict) -> None:
        self._person_state = PersonTransformState()

    def end_handle_person(self, *, person_data: dict) -> None:
        self._result.persons.append(Person(
            id=person_data['id'],
            full_name=person_data['full_name'],
            films=[
                PersonFilm(id=film_id, roles=person_roles)
                for film_id, person_roles in self._person_state.films.items()
            ],
        ))

        self._result.last_modified = LastModified(
            modified=person_data['modified'],
            id=person_data['id'],
        )

    def handle_film_work(self, *, film_work_data: dict) -> None:
        self._person_state.films[film_work_data['id']].append(film_work_data['role'])

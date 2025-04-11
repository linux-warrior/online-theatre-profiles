from __future__ import annotations

from pydantic import computed_field

from .base import (
    Document,
    DocumentRelation,
)


class Film(Document):
    title: str
    description: str | None = None
    rating: float | None = None
    # noinspection PyDataclass
    genres: list[FilmGenre] = []
    # noinspection PyDataclass
    directors: list[FilmDirector] = []
    # noinspection PyDataclass
    actors: list[FilmActor] = []
    # noinspection PyDataclass
    writers: list[FilmWriter] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def genres_names(self) -> list[str]:
        return [genre.name for genre in self.genres]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def directors_names(self) -> list[str]:
        return [person.full_name for person in self.directors]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def actors_names(self) -> list[str]:
        return [person.full_name for person in self.actors]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def writers_names(self) -> list[str]:
        return [person.full_name for person in self.writers]


class FilmGenre(DocumentRelation):
    name: str


class FilmPerson(DocumentRelation):
    full_name: str


class FilmDirector(FilmPerson):
    pass


class FilmActor(FilmPerson):
    pass


class FilmWriter(FilmPerson):
    pass

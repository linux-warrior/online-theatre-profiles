from __future__ import annotations

from collections.abc import Iterable


class FilmWorksParser:
    film_works: Iterable[dict]

    def __init__(self, *, film_works: Iterable[dict]) -> None:
        self.film_works = film_works

    def parse(self, *, visitor: FilmWorksVisitor) -> None:
        for film_work_data in self.film_works:
            visitor.start_handle_film_work(film_work_data=film_work_data)

            for genre_data in film_work_data['genres']:
                visitor.handle_genre(genre_data=genre_data)

            for person_data in film_work_data['persons']:
                visitor.handle_person(person_data=person_data)

            visitor.end_handle_film_work(film_work_data=film_work_data)


class FilmWorksVisitor:
    def start_handle_film_work(self, *, film_work_data: dict) -> None:
        pass

    def end_handle_film_work(self, *, film_work_data: dict) -> None:
        pass

    def handle_genre(self, *, genre_data: dict) -> None:
        pass

    def handle_person(self, *, person_data: dict) -> None:
        pass


class GenresParser:
    genres: Iterable[dict]

    def __init__(self, *, genres: Iterable[dict]) -> None:
        self.genres = genres

    def parse(self, *, visitor: GenresVisitor) -> None:
        for genre_data in self.genres:
            visitor.handle_genre(genre_data=genre_data)


class GenresVisitor:
    def handle_genre(self, *, genre_data: dict) -> None:
        pass


class PersonsParser:
    persons: Iterable[dict]

    def __init__(self, *, persons: Iterable[dict]) -> None:
        self.persons = persons

    def parse(self, *, visitor: PersonsVisitor) -> None:
        for person_data in self.persons:
            visitor.start_handle_person(person_data=person_data)

            for film_work_data in person_data['film_works']:
                visitor.handle_film_work(film_work_data=film_work_data)

            visitor.end_handle_person(person_data=person_data)


class PersonsVisitor:
    def start_handle_person(self, *, person_data: dict) -> None:
        pass

    def end_handle_person(self, *, person_data: dict) -> None:
        pass

    def handle_film_work(self, *, film_work_data: dict) -> None:
        pass

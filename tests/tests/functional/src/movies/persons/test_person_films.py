from __future__ import annotations

import http
import uuid
from collections.abc import Iterable, Sequence
from typing import Any, cast
from urllib.parse import urljoin

import aiohttp
import pytest

from ....settings import settings
from ....utils.api import models as api_models
from ....utils.elasticsearch import ElasticsearchIndex
from ....utils.elasticsearch.models import (
    Film,
    FilmGenre,
    FilmPerson,
    FilmDirector,
    FilmActor,
    FilmWriter,
)
from ....utils.redis import RedisCache


class BasePersonFilmsTestCase:
    redis_cache: RedisCache
    films_index: ElasticsearchIndex[Film]
    aiohttp_session: aiohttp.ClientSession
    headers: dict
    films_count: int

    def __init__(self,
                 *,
                 redis_cache: RedisCache,
                 films_index: ElasticsearchIndex[Film],
                 aiohttp_session: aiohttp.ClientSession,
                 headers: dict,
                 films_count: int = 3) -> None:
        self.films_index = films_index
        self.aiohttp_session = aiohttp_session
        self.headers = headers
        self.redis_cache = redis_cache
        self.films_count = films_count

    async def run(self) -> None:
        films = list(self.create_films())
        await self.save_films_to_elasticsearch(films=films)
        await self._run_tests(films=films)

        await self.films_index.delete_index()
        await self._run_tests(films=films)

        await self.redis_cache.clear()
        await self._run_tests(films=films, empty_results=True)

    async def _run_tests(self, *, films: Iterable[Film], empty_results: bool = False) -> None:
        for role in ['director', 'actor', 'writer']:
            await self._run_tests_for_role(films=films, empty_results=empty_results, role=role)

    async def _run_tests_for_role(self, *, films: Iterable[Film], empty_results: bool = False, role: str) -> None:
        film_person = self.get_film_person(films=films, role=role)
        person_id = film_person.id if film_person is not None else None
        person_films_results = await self.get_person_films_results(person_id=person_id)

        if empty_results:
            assert person_films_results == []
            return

        person_films = list(self.get_expected_person_films(films=films, person_id=person_id))
        self.validate_person_films_results(
            person_films=person_films,
            person_films_results=person_films_results,
        )

    def create_films(self) -> Iterable[Film]:
        return self._generate_films(count=self.films_count)

    def _generate_films(self, *, count: int = 1) -> Iterable[Film]:
        ratings = [8.0, 9.0, 10.0]
        genres = [FilmGenre(name='Жанр %i') for _i in range(1, 4)]
        directors = [FilmDirector(full_name='Режиссер %i') for _i in range(1, 4)]
        actors = [FilmActor(full_name='Актер %i') for _i in range(1, 4)]
        writers = [FilmWriter(full_name='Сценарист %i') for _i in range(1, 4)]

        for i in range(1, count + 1):
            choice_index = (i - 1) % 3

            yield Film(
                title=f'Фильм {i}',
                description=f'Описание {i}',
                rating=ratings[choice_index],
                genres=[genres[choice_index]],
                directors=[directors[choice_index]],
                actors=[actors[choice_index]],
                writers=[writers[choice_index]],
            )

    async def save_films_to_elasticsearch(self, *, films: list[Film]) -> None:
        if not films:
            return

        await self.films_index.load_documents(documents=films)

    def get_film_person(self, *, films: Iterable[Film], role: str) -> FilmPerson | None:
        for film in films:
            film_persons_list: Sequence[FilmPerson]

            if role == 'director':
                film_persons_list = film.directors
            elif role == 'actor':
                film_persons_list = film.actors
            elif role == 'writer':
                film_persons_list = film.writers
            else:
                return None

            if film_persons_list:
                return film_persons_list[0]

        return None

    async def get_person_films_results(self, *, person_id: uuid.UUID | None) -> list[dict]:
        if person_id is None:
            return []

        return await self._download_person_films(person_id=person_id)

    async def _download_person_films(self, *, person_id: uuid.UUID) -> list[dict]:
        return await self._get_person_films_response_data(person_id=str(person_id))

    async def _get_person_films_response_data(self,
                                              *,
                                              person_id: str,
                                              expected_status: int = http.HTTPStatus.OK) -> Any:
        person_films_api_url = urljoin(settings.movies_api_url, f'v1/persons/{person_id}/film/')

        async with self.aiohttp_session.get(person_films_api_url, headers=self.headers) as response:
            assert response.status == expected_status
            response_data = await response.json()

        return response_data

    def get_expected_person_films(self, *, films: Iterable[Film], person_id: uuid.UUID | None) -> Iterable[Film]:
        if person_id is None:
            return

        for film in films:
            for film_persons_list in cast(Iterable[Iterable[FilmPerson]], [
                film.directors,
                film.actors,
                film.writers,
            ]):
                if any(film_person.id == person_id for film_person in film_persons_list):
                    yield film

    def validate_person_films_results(self,
                                      *,
                                      person_films: Iterable[Film],
                                      person_films_results: Iterable[dict]) -> None:
        person_films_results_dict: dict[str, dict] = {
            person_film_result_data['uuid']: person_film_result_data
            for person_film_result_data in person_films_results
        }

        expected_person_films_results_dict: dict[str, dict] = {}
        for film in person_films:
            expected_person_film_result = api_models.PersonFilm(**film.model_dump())
            expected_person_film_result_data = expected_person_film_result.model_dump(mode='json', by_alias=True)
            expected_person_films_results_dict[expected_person_film_result_data['uuid']] = (
                expected_person_film_result_data
            )

        assert person_films_results_dict == expected_person_films_results_dict


class PersonFilmsListEmptyTestCase(BasePersonFilmsTestCase):
    def __init__(self, **kwargs: Any) -> None:
        kwargs['films_count'] = 0
        super().__init__(**kwargs)


class PersonFilmsTestCase(BasePersonFilmsTestCase):
    pass


class PersonFilmsNotFoundTestCase(BasePersonFilmsTestCase):
    async def get_person_films_results(self, *, person_id: uuid.UUID | None) -> list[dict]:
        assert await self._download_person_films(person_id=uuid.uuid4()) == []
        await self._get_person_films_response_data(
            person_id='invalid',
            expected_status=http.HTTPStatus.UNPROCESSABLE_ENTITY,
        )

        return []

    def get_expected_person_films(self, *, films: Iterable[Film], person_id: uuid.UUID | None) -> Iterable[Film]:
        return []


@pytest.mark.asyncio(loop_scope='session')
async def test_person_films_list_empty(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
) -> None:
    films_index = await create_elasticsearch_index(index_name='films')

    await PersonFilmsListEmptyTestCase(
        redis_cache=redis_cache,
        films_index=films_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_person_films(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
) -> None:
    films_index = await create_elasticsearch_index(index_name='films')

    await PersonFilmsTestCase(
        redis_cache=redis_cache,
        films_index=films_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_person_films_not_found(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
) -> None:
    films_index = await create_elasticsearch_index(index_name='films')

    await PersonFilmsNotFoundTestCase(
        redis_cache=redis_cache,
        films_index=films_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
    ).run()

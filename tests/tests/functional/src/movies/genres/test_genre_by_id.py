from __future__ import annotations

import http
import uuid
from collections.abc import Iterable
from typing import Any
from urllib.parse import urljoin

import aiohttp
import pytest

from ....settings import settings
from ....utils.api import models as api_models
from ....utils.elasticsearch import ElasticsearchIndex
from ....utils.elasticsearch.models import Genre
from ....utils.redis import RedisCache


class BaseGenreByIdTestCase:
    redis_cache: RedisCache
    genres_index: ElasticsearchIndex[Genre]
    aiohttp_session: aiohttp.ClientSession
    headers: dict
    genres_count: int

    def __init__(self,
                 *,
                 redis_cache: RedisCache,
                 genres_index: ElasticsearchIndex[Genre],
                 aiohttp_session: aiohttp.ClientSession,
                 headers: dict,
                 genres_count: int = 10
                 ) -> None:
        self.genres_index = genres_index
        self.aiohttp_session = aiohttp_session
        self.redis_cache = redis_cache
        self.headers = headers
        self.genres_count = genres_count

    async def run(self) -> None:
        genres = list(self.create_genres())
        await self.save_genres_to_elasticsearch(genres=genres)

        genre = self.get_genre(genres=genres)
        genre_id = genre.id if genre is not None else None

        genre_result_data = await self.get_genre_result(genre_id=genre_id)
        self.validate_genre_result(genre=genre, genre_result_data=genre_result_data)

        await self.genres_index.delete_index()

        genre_result_data = await self.get_genre_result(genre_id=genre_id)
        self.validate_genre_result(genre=genre, genre_result_data=genre_result_data)

        await self.redis_cache.clear()


        genre_result_data = await self.get_genre_result(genre_id=genre_id, expected_status=http.HTTPStatus.NOT_FOUND)
        assert genre_result_data is None

    def create_genres(self) -> Iterable[Genre]:
        return self._generate_genres(count=self.genres_count)

    def _generate_genres(self, *, count: int = 1) -> Iterable[Genre]:
        for i in range(1, count + 1):
            yield Genre(name=f'Жанр {i}')

    async def save_genres_to_elasticsearch(self, *, genres: list[Genre]) -> None:
        if not genres:
            return

        await self.genres_index.load_documents(documents=genres)

    def get_genre(self, *, genres: list[Genre]) -> Genre | None:
        if not genres:
            return None

        return genres[0]

    async def get_genre_result(self,
                               *,
                               genre_id: uuid.UUID | None,
                               expected_status: int = http.HTTPStatus.OK) -> dict | None:
        if genre_id is None:
            return None

        return await self._download_genre(genre_id=genre_id, expected_status=expected_status)

    async def _download_genre(self, *, genre_id: uuid.UUID, expected_status: int = http.HTTPStatus.OK) -> dict | None:
        response_data = await self._get_genre_response_data(
            genre_id=str(genre_id),
            expected_status=expected_status,
        )

        if expected_status == http.HTTPStatus.NOT_FOUND:
            return None

        return response_data

    async def _get_genre_response_data(self,
                                       *,
                                       genre_id: str,
                                       expected_status: int = http.HTTPStatus.OK) -> Any:
        genre_by_id_api_url = urljoin(settings.movies_api_url, f'v1/genres/{genre_id}')

        async with self.aiohttp_session.get(genre_by_id_api_url, headers=self.headers) as response:
            assert response.status == expected_status
            response_data = await response.json()

        return response_data

    def validate_genre_result(self, *, genre: Genre | None, genre_result_data: dict | None) -> None:
        if genre is None:
            assert genre_result_data is None
            return

        expected_genre_result = api_models.Genre(**genre.model_dump())
        expected_genre_result_data = expected_genre_result.model_dump(mode='json', by_alias=True)

        assert genre_result_data == expected_genre_result_data


class GenreByIdTestCase(BaseGenreByIdTestCase):
    pass


class GenreDoesNotExistTestCase(BaseGenreByIdTestCase):
    def get_genre(self, *, genres: list[Genre]) -> Genre | None:
        return None

    async def get_genre_result(self,
                               *,
                               genre_id: uuid.UUID | None,
                               expected_status: int = http.HTTPStatus.OK) -> dict | None:
        await self._download_genre(
            genre_id=uuid.uuid4(),
            expected_status=http.HTTPStatus.NOT_FOUND,
        )
        await self._get_genre_response_data(
            genre_id='invalid',
            expected_status=http.HTTPStatus.UNPROCESSABLE_ENTITY,
        )

        return None


@pytest.mark.asyncio(loop_scope='session')
async def test_genre_by_id(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers
) -> None:
    genres_index = await create_elasticsearch_index(index_name='genres')

    await GenreByIdTestCase(
        redis_cache=redis_cache,
        genres_index=genres_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_genre_does_not_exist(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
) -> None:
    genres_index = await create_elasticsearch_index(index_name='genres')

    await GenreDoesNotExistTestCase(
        redis_cache=redis_cache,
        genres_index=genres_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
    ).run()

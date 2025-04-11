from __future__ import annotations

import http
from collections.abc import Iterable
from typing import Any
from urllib.parse import urljoin

import aiohttp
import aiohttp.typedefs
import math
import pytest

from ....settings import settings
from ....utils.api import models as api_models
from ....utils.elasticsearch import ElasticsearchIndex
from ....utils.elasticsearch.models import Genre
from ....utils.redis import RedisCache


class BaseGenresListTestCase:
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
                 genres_count: int) -> None:
        self.genres_index = genres_index
        self.aiohttp_session = aiohttp_session
        self.headers = headers
        self.redis_cache = redis_cache
        self.genres_count = genres_count

    async def run(self) -> None:
        genres = list(self.create_genres())
        await self.save_genres_to_elasticsearch(genres=genres)

        genres_results = await self.get_genres_results()
        self.validate_genres_results(genres=genres, genres_results=genres_results)

        await self.genres_index.delete_index()

        genres_results = await self.get_genres_results()
        self.validate_genres_results(genres=genres, genres_results=genres_results)

        await self.redis_cache.clear()

        genres_results = await self.get_genres_results()
        assert genres_results == []

    def create_genres(self) -> Iterable[Genre]:
        return self._generate_genres(count=self.genres_count)

    def _generate_genres(self, *, count: int = 1) -> Iterable[Genre]:
        for i in range(1, count + 1):
            yield Genre(name=f'Жанр {i}')

    async def save_genres_to_elasticsearch(self, *, genres: list[Genre]) -> None:
        if not genres:
            return

        await self.genres_index.load_documents(documents=genres)

    async def get_genres_results(self) -> list[dict]:
        return await self._download_genres_list()

    async def _download_genres_list(self,
                                    *,
                                    page_size: int | None = None,
                                    page_number: int | None = None) -> list[dict]:
        params = {
            'page_size': page_size,
            'page_number': page_number,
        }

        return await self._get_genres_list_response_data(params={
            key: value for key, value in params.items() if value is not None
        })

    async def _get_genres_list_response_data(self,
                                             *,
                                             params: aiohttp.typedefs.Query | None = None,
                                             expected_status: int = http.HTTPStatus.OK) -> Any:
        genres_list_api_url = urljoin(settings.movies_api_url, 'v1/genres/')

        async with self.aiohttp_session.get(
                genres_list_api_url,
                headers=self.headers,
                params=params
        ) as response:
            assert response.status == expected_status
            response_data = await response.json()

        return response_data

    def validate_genres_results(self, *, genres: Iterable[Genre], genres_results: Iterable[dict]) -> None:
        genres_results_dict: dict[str, dict] = {
            genre_result_data['uuid']: genre_result_data for genre_result_data in genres_results
        }

        expected_genres_results_dict: dict[str, dict] = {}
        for genre in genres:
            expected_genre_result = api_models.Genre(**genre.model_dump())
            expected_genre_result_data = expected_genre_result.model_dump(mode='json', by_alias=True)
            expected_genres_results_dict[expected_genre_result_data['uuid']] = expected_genre_result_data

        assert genres_results_dict == expected_genres_results_dict


class GenresListEmptyTestCase(BaseGenresListTestCase):
    def __init__(self, **kwargs: Any) -> None:
        kwargs['genres_count'] = 0
        super().__init__(**kwargs)


class GenresListSinglePageTestCase(BaseGenresListTestCase):
    pass


class GenresListMultiplePagesTestCase(BaseGenresListTestCase):
    page_size: int

    def __init__(self, *, page_size: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.page_size = page_size

    async def get_genres_results(self) -> list[dict]:
        pages_count = math.ceil(self.genres_count / self.page_size)
        genres_results: list[dict] = []

        for page_number in range(1, pages_count + 1):
            genres_results += await self._download_genres_list(
                page_size=self.page_size,
                page_number=page_number,
            )

        empty_page_genres_results = await self._download_genres_list(
            page_size=self.page_size,
            page_number=pages_count + 1,
        )
        assert empty_page_genres_results == []

        for invalid_params in [
            {
                'page_size': 'invalid',
            },
            {
                'page_number': 'invalid',
            },
        ]:
            await self._get_genres_list_response_data(
                params=invalid_params,
                expected_status=http.HTTPStatus.UNPROCESSABLE_ENTITY,
            )

        return genres_results


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_list_empty(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
) -> None:
    genres_index = await create_elasticsearch_index(index_name='genres')

    await GenresListEmptyTestCase(
        redis_cache=redis_cache,
        genres_index=genres_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_list_single_page(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
) -> None:
    genres_index = await create_elasticsearch_index(index_name='genres')

    await GenresListSinglePageTestCase(
        redis_cache=redis_cache,
        genres_index=genres_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
        genres_count=10,
    ).run()


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_list_multiple_pages(
        redis_cache,
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
) -> None:
    genres_index = await create_elasticsearch_index(index_name='genres')

    await GenresListMultiplePagesTestCase(
        redis_cache=redis_cache,
        genres_index=genres_index,
        aiohttp_session=aiohttp_session,
        headers=auth_headers,
        genres_count=25,
        page_size=10,
    ).run()

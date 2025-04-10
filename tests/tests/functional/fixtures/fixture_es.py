from __future__ import annotations

from collections.abc import Callable, Awaitable, AsyncGenerator

import elasticsearch
import pytest_asyncio


from ..data.elasticsearch.schema import indices_data
from ..settings import settings
from ..utils.elasticsearch import ElasticsearchIndex


@pytest_asyncio.fixture(scope='session')
async def elasticsearch_client() -> AsyncGenerator[elasticsearch.AsyncElasticsearch]:
    async with elasticsearch.AsyncElasticsearch(settings.elasticsearch.url) as elasticsearch_client:
        yield elasticsearch_client


@pytest_asyncio.fixture
async def create_elasticsearch_index(
        elasticsearch_client: elasticsearch.AsyncElasticsearch,
) -> AsyncGenerator[Callable[..., Awaitable[ElasticsearchIndex]]]:
    elasticsearch_indices_registry: dict[str, ElasticsearchIndex] = {}

    async def _create_elasticsearch_index(*, index_name: str) -> ElasticsearchIndex:
        index_data = indices_data.get(index_name)
        if index_data is None:
            raise ValueError('Указан неизвестный индекс Elasticsearch')

        elasticsearch_index = elasticsearch_indices_registry.get(index_name)
        if elasticsearch_index is not None:
            return elasticsearch_index

        elasticsearch_index = ElasticsearchIndex(
            client=elasticsearch_client,
            index_name=index_name,
            index_data=index_data,
        )
        elasticsearch_indices_registry[index_name] = elasticsearch_index
        await elasticsearch_index.create_index(recreate=True)

        return elasticsearch_index

    yield _create_elasticsearch_index

    for _elasticsearch_index in elasticsearch_indices_registry.values():
        await _elasticsearch_index.delete_index()

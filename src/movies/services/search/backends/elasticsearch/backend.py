from __future__ import annotations

from typing import Annotated

import backoff
import elasticsearch
from fastapi import Depends

from .query import (
    CompiledElasticsearchGetQuery,
    CompiledElasticsearchSearchQuery,
    ElasticsearchQueryFactory,
)
from ..base import AbstractSearchBackend
from .....db import ElasticsearchClientDep


class ElasticsearchSearchBackend(AbstractSearchBackend):
    _elasticsearch_client: elasticsearch.AsyncElasticsearch
    _query_factory: ElasticsearchQueryFactory

    def __init__(self, *, elasticsearch_client: elasticsearch.AsyncElasticsearch) -> None:
        self._elasticsearch_client = elasticsearch_client
        self._query_factory = ElasticsearchQueryFactory(backend=self)

    def create_query(self) -> ElasticsearchQueryFactory:
        return self._query_factory

    @backoff.on_exception(backoff.expo, (
            elasticsearch.exceptions.ConnectionError,
            elasticsearch.exceptions.ConnectionTimeout,
    ))
    async def get(self, query: CompiledElasticsearchGetQuery) -> dict | None:
        try:
            response = await self._elasticsearch_client.get(index=query.index, id=query.id)
        except elasticsearch.NotFoundError:
            return None

        return response['_source']

    @backoff.on_exception(backoff.expo, (
            elasticsearch.exceptions.ConnectionError,
            elasticsearch.exceptions.ConnectionTimeout,
    ))
    async def search(self, query: CompiledElasticsearchSearchQuery) -> list[dict] | None:
        try:
            response = await self._elasticsearch_client.search(index=query.index, body=query.body)
        except elasticsearch.NotFoundError:
            return None

        results = response['hits']['hits']

        if not results:
            return None

        return [result['_source'] for result in results]


async def get_search_backend(elasticsearch_client: ElasticsearchClientDep) -> ElasticsearchSearchBackend:
    return ElasticsearchSearchBackend(elasticsearch_client=elasticsearch_client)


ElasticsearchSearchBackendDep = Annotated[ElasticsearchSearchBackend, Depends(get_search_backend)]

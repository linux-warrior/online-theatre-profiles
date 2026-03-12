from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from ...base import (
    AbstractGetQuery,
    AbstractCompiledGetQuery,
    AbstractSearchQuery,
    AbstractCompiledSearchQuery,
)

if TYPE_CHECKING:
    from ..backend import ElasticsearchSearchBackend


class ElasticsearchGetQuery(AbstractGetQuery):
    _backend: ElasticsearchSearchBackend

    def __init__(self, *, backend: ElasticsearchSearchBackend) -> None:
        self._backend = backend

    def compile(self) -> CompiledElasticsearchGetQuery:
        return CompiledElasticsearchGetQuery(
            backend=self._backend,
            index=self.get_index(),
            id=self.get_id(),
        )

    @abc.abstractmethod
    def get_index(self) -> str: ...

    @abc.abstractmethod
    def get_id(self) -> str: ...


class CompiledElasticsearchGetQuery(AbstractCompiledGetQuery):
    _backend: ElasticsearchSearchBackend
    _index: str
    _id: str

    def __init__(self,
                 *,
                 backend: ElasticsearchSearchBackend,
                 index: str,
                 id: str) -> None:
        self._backend = backend
        self._index = index
        self._id = id

    @property
    def index(self) -> str:
        return self._index

    @property
    def id(self) -> str:
        return self._id

    async def execute(self) -> dict | None:
        return await self._backend.get(self)

    def get_cache_prefix(self) -> str:
        return f'get-{self._index}'

    def get_cache_params(self) -> dict:
        return {
            'command': 'get',
            'index': self._index,
            'id': self._id,
        }


class ElasticsearchSearchQuery(AbstractSearchQuery):
    _backend: ElasticsearchSearchBackend

    def __init__(self, *, backend: ElasticsearchSearchBackend) -> None:
        self._backend = backend

    def compile(self) -> CompiledElasticsearchSearchQuery:
        return CompiledElasticsearchSearchQuery(
            backend=self._backend,
            index=self.get_index(),
            body=self.get_body(),
        )

    @abc.abstractmethod
    def get_index(self) -> str: ...

    @abc.abstractmethod
    def get_body(self) -> dict: ...


class CompiledElasticsearchSearchQuery(AbstractCompiledSearchQuery):
    _backend: ElasticsearchSearchBackend
    _index: str
    _body: dict

    def __init__(self,
                 *,
                 backend: ElasticsearchSearchBackend,
                 index: str,
                 body: dict) -> None:
        self._backend = backend
        self._index = index
        self._body = body

    @property
    def index(self) -> str:
        return self._index

    @property
    def body(self) -> dict:
        return self._body

    async def execute(self) -> list[dict] | None:
        return await self._backend.search(self)

    def get_cache_prefix(self) -> str:
        return f'search-{self._index}'

    def get_cache_params(self) -> dict:
        return {
            'command': 'search',
            'index': self._index,
            'body': self._body,
        }

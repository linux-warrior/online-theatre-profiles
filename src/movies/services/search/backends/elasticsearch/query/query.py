from __future__ import annotations

import abc
import dataclasses
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
    backend: ElasticsearchSearchBackend

    def __init__(self, *, backend: ElasticsearchSearchBackend) -> None:
        self.backend = backend

    def compile(self) -> CompiledElasticsearchGetQuery:
        return CompiledElasticsearchGetQuery(
            backend=self.backend,
            index=self.get_index(),
            id=self.get_id(),
        )

    @abc.abstractmethod
    def get_index(self) -> str: ...

    @abc.abstractmethod
    def get_id(self) -> str: ...


@dataclasses.dataclass(kw_only=True)
class CompiledElasticsearchGetQuery(AbstractCompiledGetQuery):
    backend: ElasticsearchSearchBackend
    index: str
    id: str

    async def execute(self) -> dict | None:
        return await self.backend.get(self)

    def get_cache_prefix(self) -> str:
        return f'get-{self.index}'

    def get_cache_params(self) -> dict:
        return {
            'command': 'get',
            'index': self.index,
            'id': self.id,
        }


class ElasticsearchSearchQuery(AbstractSearchQuery):
    backend: ElasticsearchSearchBackend

    def __init__(self, *, backend: ElasticsearchSearchBackend) -> None:
        self.backend = backend

    def compile(self) -> CompiledElasticsearchSearchQuery:
        return CompiledElasticsearchSearchQuery(
            backend=self.backend,
            index=self.get_index(),
            body=self.get_body(),
        )

    @abc.abstractmethod
    def get_index(self) -> str: ...

    @abc.abstractmethod
    def get_body(self) -> dict: ...


@dataclasses.dataclass(kw_only=True)
class CompiledElasticsearchSearchQuery(AbstractCompiledSearchQuery):
    backend: ElasticsearchSearchBackend
    index: str
    body: dict

    async def execute(self) -> list[dict] | None:
        return await self.backend.search(self)

    def get_cache_prefix(self) -> str:
        return f'search-{self.index}'

    def get_cache_params(self) -> dict:
        return {
            'command': 'search',
            'index': self.index,
            'body': self.body,
        }

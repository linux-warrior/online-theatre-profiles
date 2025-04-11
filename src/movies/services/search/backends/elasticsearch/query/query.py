from __future__ import annotations

import abc
import dataclasses

from ...base import (
    AbstractGetQuery,
    AbstractCompiledGetQuery,
    AbstractSearchQuery,
    AbstractCompiledSearchQuery,
)


class ElasticsearchGetQuery(AbstractGetQuery):
    def compile(self) -> CompiledElasticsearchGetQuery:
        return CompiledElasticsearchGetQuery(
            index=self.get_index(),
            id=self.get_id(),
        )

    @abc.abstractmethod
    def get_index(self) -> str: ...

    @abc.abstractmethod
    def get_id(self) -> str: ...


@dataclasses.dataclass(kw_only=True)
class CompiledElasticsearchGetQuery(AbstractCompiledGetQuery):
    index: str
    id: str

    def get_cache_prefix(self) -> str:
        return f'get-{self.index}'

    def get_cache_params(self) -> dict:
        return {
            'command': 'get',
            'index': self.index,
            'id': self.id,
        }


class ElasticsearchSearchQuery(AbstractSearchQuery):
    def compile(self) -> CompiledElasticsearchSearchQuery:
        return CompiledElasticsearchSearchQuery(
            index=self.get_index(),
            body=self.get_body(),
        )

    @abc.abstractmethod
    def get_index(self) -> str: ...

    @abc.abstractmethod
    def get_body(self) -> dict: ...


@dataclasses.dataclass(kw_only=True)
class CompiledElasticsearchSearchQuery(AbstractCompiledSearchQuery):
    index: str
    body: dict

    def get_cache_prefix(self) -> str:
        return f'search-{self.index}'

    def get_cache_params(self) -> dict:
        return {
            'command': 'search',
            'index': self.index,
            'body': self.body,
        }

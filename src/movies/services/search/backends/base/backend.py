from __future__ import annotations

import abc

from .query import (
    AbstractCompiledGetQuery,
    AbstractCompiledSearchQuery,
    AbstractQueryFactory,
)


class AbstractSearchBackend(abc.ABC):
    @abc.abstractmethod
    async def get(self, *, query: AbstractCompiledGetQuery) -> dict | None: ...

    @abc.abstractmethod
    async def search(self, *, query: AbstractCompiledSearchQuery) -> list[dict] | None: ...

    @abc.abstractmethod
    def create_query(self) -> AbstractQueryFactory: ...

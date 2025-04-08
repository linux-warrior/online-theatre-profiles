from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from .....cache import Parameterizable

if TYPE_CHECKING:
    from ..backend import AbstractSearchBackend


class AbstractQuery[TResult](abc.ABC):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledQuery[TResult]: ...


class AbstractCompiledQuery[TResult](Parameterizable):
    @abc.abstractmethod
    async def execute(self, *, backend: AbstractSearchBackend) -> TResult: ...


class AbstractGetQuery(AbstractQuery[dict | None]):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledGetQuery: ...


class AbstractCompiledGetQuery(AbstractCompiledQuery[dict | None], abc.ABC):
    async def execute(self, *, backend: AbstractSearchBackend) -> dict | None:
        return await backend.get(query=self)


class AbstractSearchQuery(AbstractQuery[list[dict] | None]):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledSearchQuery: ...


class AbstractCompiledSearchQuery(AbstractCompiledQuery[list[dict] | None], abc.ABC):
    async def execute(self, *, backend: AbstractSearchBackend) -> list[dict] | None:
        return await backend.search(query=self)

from __future__ import annotations

import abc

from .....cache import Parameterizable


class AbstractQuery[TResult](abc.ABC):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledQuery[TResult]: ...


class AbstractCompiledQuery[TResult](Parameterizable):
    @abc.abstractmethod
    async def execute(self) -> TResult: ...


class AbstractGetQuery(AbstractQuery[dict | None]):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledGetQuery: ...


class AbstractCompiledGetQuery(AbstractCompiledQuery[dict | None], abc.ABC):
    pass


class AbstractSearchQuery(AbstractQuery[list[dict] | None]):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledSearchQuery: ...


class AbstractCompiledSearchQuery(AbstractCompiledQuery[list[dict] | None], abc.ABC):
    pass

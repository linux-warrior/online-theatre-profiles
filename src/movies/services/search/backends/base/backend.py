from __future__ import annotations

import abc

from .query import (
    AbstractQueryFactory,
)


class AbstractSearchBackend(abc.ABC):
    @abc.abstractmethod
    def create_query(self) -> AbstractQueryFactory: ...

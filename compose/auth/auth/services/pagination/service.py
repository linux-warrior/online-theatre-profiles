from __future__ import annotations

import abc
import datetime
import uuid
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import (
    Select,
    SQLColumnExpression,
)

from .paginator import (
    AbstractPaginator,
    Paginator,
)


class AbstractPaginationService(abc.ABC):
    @abc.abstractmethod
    def get_paginator[TSelectable: tuple[Any, ...]](
            self,
            *,
            statement: Select[TSelectable],
            id_column: SQLColumnExpression[uuid.UUID],
            timestamp_column: SQLColumnExpression[datetime.datetime]) -> AbstractPaginator[TSelectable]: ...


class PaginationService(AbstractPaginationService):
    def get_paginator[TSelectable: tuple[Any, ...]](
            self,
            *,
            statement: Select[TSelectable],
            id_column: SQLColumnExpression[uuid.UUID],
            timestamp_column: SQLColumnExpression[datetime.datetime]) -> AbstractPaginator[TSelectable]:
        return Paginator(
            statement=statement,
            id_column=id_column,
            timestamp_column=timestamp_column,
        )


async def get_pagination_service() -> AbstractPaginationService:
    return PaginationService()


PaginationServiceDep = Annotated[AbstractPaginationService, Depends(get_pagination_service)]

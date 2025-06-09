from __future__ import annotations

import abc
import datetime
import uuid
from typing import Any

from sqlalchemy import (
    and_,
    or_,
    true,
    Select,
    SQLColumnExpression,
    ColumnElement,
)

from .models import PageParams


class AbstractPaginator[TSelectable: tuple[Any, ...]](abc.ABC):
    @abc.abstractmethod
    def get_page(self, *, page_params: PageParams) -> Select[TSelectable]: ...


class Paginator[TSelectable: tuple[Any, ...]](AbstractPaginator[TSelectable]):
    page_size: int = 100

    statement: Select[TSelectable]
    id_column: SQLColumnExpression[uuid.UUID]
    timestamp_column: SQLColumnExpression[datetime.datetime]

    def __init__(self,
                 *,
                 statement: Select[TSelectable],
                 id_column: SQLColumnExpression[uuid.UUID],
                 timestamp_column: SQLColumnExpression[datetime.datetime],
                 page_size: int | None = None) -> None:
        self.statement = statement
        self.id_column = id_column
        self.timestamp_column = timestamp_column
        self.page_size = page_size or self.page_size

    def get_page(self, *, page_params: PageParams) -> Select[TSelectable]:
        timestamp_clauses: list[ColumnElement[bool]] = []

        if page_params.timestamp is not None:
            timestamp_clauses.append(
                self.timestamp_column < page_params.timestamp,
            )

        if page_params.timestamp is not None and page_params.id is not None:
            timestamp_clauses.append(
                and_(
                    self.timestamp_column == page_params.timestamp,
                    self.id_column < page_params.id,
                ),
            )

        page_size = page_params.size or self.page_size

        return self.statement.where(
            or_(*timestamp_clauses) if timestamp_clauses else true(),
        ).limit(
            page_size,
        ).order_by(
            self.timestamp_column.desc(),
            self.id_column.desc(),
        )

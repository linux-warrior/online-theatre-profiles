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

from .models import (
    PageParams,
    SortOrder,
)


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
        is_descending = page_params.sort_order == SortOrder.DESC

        if page_params.timestamp is not None:
            timestamp_comparison_clause: ColumnElement[bool]

            if is_descending:
                timestamp_comparison_clause = self.timestamp_column < page_params.timestamp
            else:
                timestamp_comparison_clause = self.timestamp_column > page_params.timestamp

            timestamp_clauses.append(timestamp_comparison_clause)

        if page_params.timestamp is not None and page_params.id is not None:
            id_comparison_clause: ColumnElement[bool]

            if is_descending:
                id_comparison_clause = self.id_column < page_params.id
            else:
                id_comparison_clause = self.id_column > page_params.id

            timestamp_clauses.append(and_(
                self.timestamp_column == page_params.timestamp,
                id_comparison_clause,
            ))

        page_order_by_clauses: list[SQLColumnExpression[Any]] = [
            self.timestamp_column,
            self.id_column,
        ]

        if is_descending:
            page_order_by_clauses = [order_by_clause.desc() for order_by_clause in page_order_by_clauses]

        return self.statement.where(
            or_(*timestamp_clauses) if timestamp_clauses else true(),
        ).limit(
            page_params.size or self.page_size,
        ).order_by(
            *page_order_by_clauses,
        )

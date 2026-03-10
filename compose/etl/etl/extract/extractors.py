from __future__ import annotations

from collections.abc import Iterable
from typing import ClassVar

import backoff
import psycopg
import psycopg.abc
import psycopg.rows

from .query import (
    ExtractSQLStatement,
    ExtractFilmWorksSQLStatement,
    ExtractGenresSQLStatement,
    ExtractPersonsSQLStatement,
)
from ..state import LastModified


class PostgreSQLConnectionFactory:
    _connection_params: dict

    def __init__(self, *, connection_params: dict) -> None:
        self._connection_params = connection_params

    @backoff.on_exception(backoff.expo, psycopg.OperationalError)
    def create(self) -> psycopg.Connection[dict]:
        return psycopg.connect(**self._connection_params, row_factory=psycopg.rows.dict_row)


class PostgreSQLCursorExecutor:
    _cursor: psycopg.Cursor[dict]

    def __init__(self, *, cursor: psycopg.Cursor[dict]) -> None:
        self._cursor = cursor

    @backoff.on_exception(backoff.expo, psycopg.OperationalError)
    def execute(self,
                *,
                query: psycopg.abc.QueryNoTemplate,
                params: psycopg.abc.Params | None = None) -> psycopg.Cursor[dict]:
        return self._cursor.execute(query, params)


class PostgreSQLExtractor:
    batch_size: ClassVar[int] = 100
    extract_sql_statement_class: ClassVar[type[ExtractSQLStatement]]

    _connection_factory: PostgreSQLConnectionFactory
    _batch_size: int
    _extract_sql_statement: ExtractSQLStatement

    def __init__(self, *, connection_params: dict, batch_size: int | None = None) -> None:
        self._connection_factory = PostgreSQLConnectionFactory(connection_params=connection_params)
        self._batch_size = batch_size or self.batch_size
        self._extract_sql_statement = self.extract_sql_statement_class(batch_size=self._batch_size)

    def extract(self, *, last_modified: LastModified) -> Iterable[dict]:
        with self._connection_factory.create() as connection:
            with connection.cursor() as cursor:
                cursor_executor = PostgreSQLCursorExecutor(cursor=cursor)
                query = self._extract_sql_statement.compile(last_modified=last_modified)
                yield from cursor_executor.execute(query=query)


class FilmWorksExtractor(PostgreSQLExtractor):
    extract_sql_statement_class = ExtractFilmWorksSQLStatement


class GenresExtractor(PostgreSQLExtractor):
    extract_sql_statement_class = ExtractGenresSQLStatement


class PersonsExtractor(PostgreSQLExtractor):
    extract_sql_statement_class = ExtractPersonsSQLStatement

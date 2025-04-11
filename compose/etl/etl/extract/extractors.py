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
    connection_params: dict

    def __init__(self, *, connection_params: dict) -> None:
        self.connection_params = connection_params

    @backoff.on_exception(backoff.expo, psycopg.OperationalError)
    def create(self) -> psycopg.Connection[dict]:
        return psycopg.connect(**self.connection_params, row_factory=psycopg.rows.dict_row)


class PostgreSQLCursorExecutor:
    cursor: psycopg.Cursor[dict]

    def __init__(self, *, cursor: psycopg.Cursor[dict]) -> None:
        self.cursor = cursor

    @backoff.on_exception(backoff.expo, psycopg.OperationalError)
    def execute(self,
                *,
                query: psycopg.abc.Query,
                params: psycopg.abc.Params | None = None) -> psycopg.Cursor[dict]:
        return self.cursor.execute(query, params)


class PostgreSQLExtractor:
    batch_size: int = 100
    extract_sql_statement_class: ClassVar[type[ExtractSQLStatement]]

    connection_factory: PostgreSQLConnectionFactory
    extract_sql_statement: ExtractSQLStatement

    def __init__(self, *, connection_params: dict, batch_size: int | None = None) -> None:
        self.connection_factory = PostgreSQLConnectionFactory(connection_params=connection_params)
        self.batch_size = batch_size or self.batch_size
        self.extract_sql_statement = self.extract_sql_statement_class(batch_size=self.batch_size)

    def extract(self, *, last_modified: LastModified) -> Iterable[dict]:
        with self.connection_factory.create() as connection:
            with connection.cursor() as cursor:
                cursor_executor = PostgreSQLCursorExecutor(cursor=cursor)
                query = self.extract_sql_statement.compile(last_modified=last_modified)
                yield from cursor_executor.execute(query=query)


class FilmWorksExtractor(PostgreSQLExtractor):
    extract_sql_statement_class = ExtractFilmWorksSQLStatement


class GenresExtractor(PostgreSQLExtractor):
    extract_sql_statement_class = ExtractGenresSQLStatement


class PersonsExtractor(PostgreSQLExtractor):
    extract_sql_statement_class = ExtractPersonsSQLStatement

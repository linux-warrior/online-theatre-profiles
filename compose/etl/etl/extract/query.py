from __future__ import annotations

from psycopg import sql

from ..state import LastModified


class TableModifiedCondition:
    table_name: str

    def __init__(self, *, table_name: str) -> None:
        self.table_name = table_name

    def compile(self, *, last_modified: LastModified) -> sql.Composable:
        sql_parts: list[sql.Composable] = []

        if last_modified.modified is not None:
            sql_parts.append(sql.SQL('({table_name}.modified > {last_modified})').format(
                table_name=sql.Identifier(self.table_name),
                last_modified=last_modified.modified,
            ))

        if last_modified.modified is not None and last_modified.id is not None:
            sql_parts.append(
                sql.SQL('({table_name}.modified = {last_modified} AND {table_name}.id > {last_id})').format(
                    table_name=sql.Identifier(self.table_name),
                    last_modified=last_modified.modified,
                    last_id=last_modified.id,
                ),
            )

        if not sql_parts:
            return sql.Literal('true')

        return sql.SQL('({condition})').format(
            condition=sql.SQL(' OR ').join(sql_parts),
        )


class ExtractSQLStatement:
    batch_size: int

    def __init__(self, *, batch_size: int) -> None:
        self.batch_size = batch_size

    def compile(self, *, last_modified: LastModified) -> sql.Composed:
        raise NotImplementedError


class ExtractFilmWorksSQLStatement(ExtractSQLStatement):
    table_modified_condition: TableModifiedCondition

    def __init__(self, *, batch_size: int) -> None:
        super().__init__(batch_size=batch_size)
        self.table_modified_condition = TableModifiedCondition(table_name='modified_film_work')

    def compile(self, *, last_modified: LastModified) -> sql.Composed:
        where_condition = self.table_modified_condition.compile(last_modified=last_modified)

        # noinspection SqlNoDataSourceInspection,SqlResolve
        return sql.SQL('''
            SELECT DISTINCT
                film_work.id,
                modified_film_work.modified,
                film_work.title,
                film_work.description,
                film_work.rating,
                COALESCE(jsonb_agg(DISTINCT jsonb_build_object(
                    'id', genre.id,
                    'modified', genre.modified,
                    'name', genre.name
                )) FILTER (WHERE genre.id IS NOT NULL), '[]'::jsonb) AS genres,
                COALESCE(jsonb_agg(DISTINCT jsonb_build_object(
                    'id', person.id,
                    'modified', person.modified,
                    'full_name', person.full_name,
                    'role', person_film_work.role
                )) FILTER (WHERE person.id IS NOT NULL), '[]'::jsonb) AS persons
            FROM content.film_work AS film_work
                LEFT JOIN content.genre_film_work AS genre_film_work
                    ON genre_film_work.film_work_id = film_work.id
                LEFT JOIN content.genre AS genre
                    ON genre_film_work.genre_id = genre.id
                LEFT JOIN content.person_film_work AS person_film_work
                    ON person_film_work.film_work_id = film_work.id
                LEFT JOIN content.person AS person
                    ON person_film_work.person_id = person.id
                INNER JOIN (
                    SELECT
                        film_work.id,
                        GREATEST(film_work.modified, max(genre.modified), max(person.modified)) AS modified
                    FROM content.film_work AS film_work
                    LEFT JOIN content.genre_film_work AS genre_film_work
                        ON genre_film_work.film_work_id = film_work.id
                    LEFT JOIN content.genre AS genre
                        ON genre_film_work.genre_id = genre.id
                    LEFT JOIN content.person_film_work AS person_film_work
                        ON person_film_work.film_work_id = film_work.id
                    LEFT JOIN content.person AS person
                        ON person_film_work.person_id = person.id
                    GROUP BY
                        film_work.id
                ) AS modified_film_work
                    ON film_work.id = modified_film_work.id
            WHERE {where_condition}
            GROUP BY
                film_work.id,
                modified_film_work.modified
            ORDER BY
                modified_film_work.modified,
                film_work.id
            LIMIT {batch_size}
        ''').format(
            where_condition=where_condition,
            batch_size=self.batch_size,
        )


class ExtractGenresSQLStatement(ExtractSQLStatement):
    table_modified_condition: TableModifiedCondition

    def __init__(self, *, batch_size: int) -> None:
        super().__init__(batch_size=batch_size)
        self.table_modified_condition = TableModifiedCondition(table_name='genre')

    def compile(self, *, last_modified: LastModified) -> sql.Composed:
        where_condition = self.table_modified_condition.compile(last_modified=last_modified)

        # noinspection SqlNoDataSourceInspection,SqlResolve
        return sql.SQL('''
            SELECT
                genre.id,
                genre.modified,
                genre.name
            FROM content.genre AS genre
            WHERE {where_condition}
            ORDER BY
                genre.modified,
                genre.id
            LIMIT {batch_size}
        ''').format(
            where_condition=where_condition,
            batch_size=self.batch_size,
        )


class ExtractPersonsSQLStatement(ExtractSQLStatement):
    table_modified_condition: TableModifiedCondition

    def __init__(self, *, batch_size: int) -> None:
        super().__init__(batch_size=batch_size)
        self.table_modified_condition = TableModifiedCondition(table_name='modified_person')

    def compile(self, *, last_modified: LastModified) -> sql.Composed:
        where_condition = self.table_modified_condition.compile(last_modified=last_modified)

        # noinspection SqlNoDataSourceInspection,SqlResolve
        return sql.SQL('''
            SELECT DISTINCT
                person.id,
                modified_person.modified,
                person.full_name,
                COALESCE(jsonb_agg(DISTINCT jsonb_build_object(
                    'id', film_work.id,
                    'modified', film_work.modified,
                    'role', person_film_work.role
                )) FILTER (WHERE film_work.id IS NOT NULL), '[]'::jsonb) AS film_works
            FROM content.person AS person
                LEFT JOIN content.person_film_work AS person_film_work
                    ON person_film_work.person_id = person.id
                LEFT JOIN content.film_work AS film_work
                    ON person_film_work.film_work_id = film_work.id
                INNER JOIN (
                    SELECT
                        person.id,
                        GREATEST(person.modified, max(film_work.modified)) AS modified
                    FROM content.person AS person
                        LEFT JOIN content.person_film_work AS person_film_work
                            ON person_film_work.person_id = person.id
                        LEFT JOIN content.film_work AS film_work
                            ON person_film_work.film_work_id = film_work.id
                    GROUP BY
                        person.id
                ) AS modified_person
                    ON person.id = modified_person.id
            WHERE {where_condition}
            GROUP BY
                person.id,
                modified_person.modified
            ORDER BY
                modified_person.modified,
                person.id
            LIMIT {batch_size}
        ''').format(
            where_condition=where_condition,
            batch_size=self.batch_size,
        )

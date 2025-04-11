from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from typing import TYPE_CHECKING

from ..extract import (
    PostgreSQLExtractor,
    FilmWorksParser,
    GenresParser,
    PersonsParser,
)
from ..load import ElasticsearchLoader
from ..state import (
    ExtractorState,
    LastModified
)
from ..transform import (
    Document,
    Film,
    Genre,
    Person,
    FilmsTransformer,
    GenresTransformer,
    PersonsTransformer,
)


@dataclasses.dataclass(kw_only=True)
class DocumentsTransformResult[TDocument: Document]:
    documents: list[TDocument]
    last_modified: LastModified

    if TYPE_CHECKING:
        # noinspection PyUnusedLocal
        def __init__(self, *, documents: list[TDocument], last_modified: LastModified) -> None: ...


class DocumentsTransformExecutor[TDocument: Document]:
    def transform_documents(self, *, documents_data: Iterable[dict]) -> DocumentsTransformResult[TDocument]:
        raise NotImplementedError


class FilmsTransformExecutor(DocumentsTransformExecutor[Film]):
    def transform_documents(self, *, documents_data: Iterable[dict]) -> DocumentsTransformResult[Film]:
        film_works_parser = FilmWorksParser(film_works=documents_data)
        films_transformer = FilmsTransformer()
        film_works_parser.parse(visitor=films_transformer)
        films_transform_result = films_transformer.get_result()

        return DocumentsTransformResult[Film](
            documents=films_transform_result.films,
            last_modified=films_transform_result.last_modified,
        )


class GenresTransformExecutor(DocumentsTransformExecutor[Genre]):
    def transform_documents(self, *, documents_data: Iterable[dict]) -> DocumentsTransformResult[Genre]:
        genres_parser = GenresParser(genres=documents_data)
        genres_transformer = GenresTransformer()
        genres_parser.parse(visitor=genres_transformer)
        genres_transform_result = genres_transformer.get_result()

        return DocumentsTransformResult[Genre](
            documents=genres_transform_result.genres,
            last_modified=genres_transform_result.last_modified,
        )


class PersonsTransformExecutor(DocumentsTransformExecutor[Person]):
    def transform_documents(self, *, documents_data: Iterable[dict]) -> DocumentsTransformResult[Person]:
        persons_parser = PersonsParser(persons=documents_data)
        persons_transformer = PersonsTransformer()
        persons_parser.parse(visitor=persons_transformer)
        persons_transform_result = persons_transformer.get_result()

        return DocumentsTransformResult[Person](
            documents=persons_transform_result.persons,
            last_modified=persons_transform_result.last_modified,
        )


class ETLPipeline[TDocument: Document]:
    extractor: PostgreSQLExtractor
    extractor_state: ExtractorState
    transform_executor: DocumentsTransformExecutor[TDocument]
    loader: ElasticsearchLoader[TDocument]

    def __init__(self,
                 *,
                 extractor: PostgreSQLExtractor,
                 extractor_state: ExtractorState,
                 transform_executor: DocumentsTransformExecutor[TDocument],
                 loader: ElasticsearchLoader[TDocument]) -> None:
        self.extractor = extractor
        self.extractor_state = extractor_state
        self.transform_executor = transform_executor
        self.loader = loader

    def transfer_data(self) -> DocumentsTransformResult[TDocument]:
        documents_data = self.extractor.extract(last_modified=self.extractor_state.last_modified)
        documents_transform_result = self.transform_executor.transform_documents(
            documents_data=documents_data,
        )

        if documents_transform_result.documents:
            self.loader.load(documents=documents_transform_result.documents)
            self.extractor_state.last_modified = documents_transform_result.last_modified

        return documents_transform_result

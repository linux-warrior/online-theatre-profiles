from __future__ import annotations

import logging
from collections.abc import Iterable

import backoff
import elasticsearch
import elasticsearch.helpers

from ..transform import Document

logger = logging.getLogger(__name__)


class ElasticsearchLoader[TDocument: Document]:
    client: elasticsearch.Elasticsearch
    index_name: str
    index_data: dict | None
    index_created: bool

    def __init__(self,
                 *,
                 client: elasticsearch.Elasticsearch,
                 index_name: str,
                 index_data: dict | None = None) -> None:
        self.client = client
        self.index_name = index_name
        self.index_data = index_data

        self.index_created = False

    @backoff.on_exception(backoff.expo, (
            elasticsearch.ConnectionError,
            elasticsearch.ConnectionTimeout,
    ))
    def load(self, *, documents: Iterable[TDocument]) -> None:
        if self.index_data and not self.index_created:
            self._create_index()

        try:
            elasticsearch.helpers.bulk(self.client, ({
                '_index': self.index_name,
                '_id': document.id,
                '_source': document.model_dump(mode='json'),
            } for document in documents))

        except elasticsearch.helpers.BulkIndexError as e:
            logger.exception(e)
            logger.debug(e.errors)
            raise

    @backoff.on_exception(backoff.expo, (
            elasticsearch.ConnectionError,
            elasticsearch.ConnectionTimeout,
    ))
    def _create_index(self) -> None:
        try:
            self.client.indices.create(index=self.index_name, body=self.index_data)
        except elasticsearch.BadRequestError as e:
            if e.error == 'resource_already_exists_exception':
                pass

        self.index_created = True

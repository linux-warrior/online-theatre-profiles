from __future__ import annotations

from collections.abc import Iterable

import elasticsearch
import elasticsearch.helpers

from .models import Document


class ElasticsearchIndex[TDocument: Document]:
    client: elasticsearch.AsyncElasticsearch
    index_name: str
    index_data: dict

    _index_created: bool

    def __init__(self,
                 *,
                 client: elasticsearch.AsyncElasticsearch,
                 index_name: str,
                 index_data: dict) -> None:
        self.client = client
        self.index_name = index_name
        self.index_data = index_data

        self._index_created = False

    async def create_index(self, *, recreate=False) -> None:
        if self._index_created and not recreate:
            return

        await self.delete_index()

        try:
            await self.client.indices.create(index=self.index_name, body=self.index_data)
        except elasticsearch.BadRequestError as e:
            if e.error == 'resource_already_exists_exception':
                pass

        self._index_created = True

    async def delete_index(self) -> None:
        try:
            await self.client.indices.delete(index=self.index_name)
        except elasticsearch.NotFoundError as e:
            if e.error == 'index_not_found_exception':
                pass

        self._index_created = False

    async def load_documents(self, *, documents: Iterable[TDocument]) -> None:
        await self.load_data(documents=(document.model_dump(mode='json') for document in documents))

    async def load_data(self, *, documents: Iterable[dict]) -> None:
        await self.create_index()
        await elasticsearch.helpers.async_bulk(self.client, ({
            '_index': self.index_name,
            '_id': document_data['id'],
            '_source': document_data,
        } for document_data in documents), refresh='wait_for')

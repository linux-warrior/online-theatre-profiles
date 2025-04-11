from __future__ import annotations

import uuid

import pytest

from ..utils.elasticsearch import ElasticsearchIndex


@pytest.mark.asyncio(loop_scope='session')
async def test_elasticsearch_indices(create_elasticsearch_index) -> None:
    elasticsearch_indices: dict[str, ElasticsearchIndex] = {}

    for index_name in [
        'films',
        'genres',
        'persons',
    ]:
        elasticsearch_indices[index_name] = await create_elasticsearch_index(
            index_name=index_name,
        )
        await elasticsearch_indices[index_name].load_data(documents=[
            {
                'id': uuid.uuid4(),
            },
        ])

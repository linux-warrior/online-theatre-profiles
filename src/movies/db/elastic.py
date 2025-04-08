from __future__ import annotations

from typing import Annotated

import elasticsearch
from fastapi import Request, Depends


async def get_elasticsearch_client(request: Request) -> elasticsearch.AsyncElasticsearch:
    return request.state.elasticsearch_client


ElasticsearchClientDep = Annotated[elasticsearch.AsyncElasticsearch, Depends(get_elasticsearch_client)]

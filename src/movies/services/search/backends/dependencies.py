from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .base import AbstractSearchBackend
from .elasticsearch import ElasticsearchSearchBackendDep


async def get_search_backend(search_backend: ElasticsearchSearchBackendDep) -> AbstractSearchBackend:
    return search_backend


SearchBackendDep = Annotated[AbstractSearchBackend, Depends(get_search_backend)]

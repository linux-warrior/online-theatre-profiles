from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .search import (
    AbstractSearchService,
    SearchServiceDep,
)
from ..models import Genre


class GenreService:
    search_service: AbstractSearchService

    def __init__(self, *, search_service: AbstractSearchService) -> None:
        self.search_service = search_service

    async def get_list(
            self,
            page_number: int,
            page_size: int,
    ) -> list[Genre]:
        search_query = self.search_service.create_query().genres_list(
            page_number=page_number,
            page_size=page_size,
        )
        result = await self.search_service.search(query=search_query)

        if result is None:
            return []

        return [Genre(**data) for data in result]

    async def get_by_id(
            self,
            id: uuid.UUID,
    ) -> Genre | None:
        get_query = self.search_service.create_query().get_genre(genre_id=id)
        data = await self.search_service.get(query=get_query)

        if not data:
            return None

        return Genre(**data)


async def get_genre_service(search_service: SearchServiceDep) -> GenreService:
    return GenreService(search_service=search_service)


GenreServiceDep = Annotated[GenreService, Depends(get_genre_service)]

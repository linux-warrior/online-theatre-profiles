from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .search import (
    AbstractSearchService,
    SearchServiceDep,
)
from ..models import Film


class FilmService:
    search_service: AbstractSearchService

    def __init__(self, *, search_service: AbstractSearchService) -> None:
        self.search_service = search_service

    async def get_list_by_person(self, person_uuid: uuid.UUID) -> list[Film]:
        search_query = self.search_service.create_query().films_by_person(person_id=person_uuid)
        result = await self.search_service.search(query=search_query)

        if result is None:
            return []

        return [Film(**data) for data in result]

    async def get_list(
            self,
            sort: dict[str, str],
            page_number: int,
            page_size: int,
            genre_uuid: uuid.UUID | None = None,
    ) -> list[Film]:
        search_query = self.search_service.create_query().films_list(
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            genre_id=genre_uuid,
        )
        result = await self.search_service.search(query=search_query)

        if result is None:
            return []

        return [Film(**data) for data in result]

    async def search(
            self,
            query: str,
            page_number: int,
            page_size: int,
    ) -> list[Film] | None:
        search_query = self.search_service.create_query().search_films(
            query=query,
            page_number=page_number,
            page_size=page_size,
        )
        result = await self.search_service.search(query=search_query)

        if result is None:
            return []

        return [Film(**data) for data in result]

    async def get_by_id(
            self,
            id: uuid.UUID,
    ) -> Film | None:
        get_query = self.search_service.create_query().get_film(film_id=id)
        data = await self.search_service.get(query=get_query)

        if not data:
            return None

        return Film(**data)


async def get_film_service(search_service: SearchServiceDep) -> FilmService:
    return FilmService(search_service=search_service)


FilmServiceDep = Annotated[FilmService, Depends(get_film_service)]

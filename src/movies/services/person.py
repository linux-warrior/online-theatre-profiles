from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .search import (
    AbstractSearchService,
    SearchServiceDep,
)
from ..models import Person


class PersonService:
    search_service: AbstractSearchService

    def __init__(self, *, search_service: AbstractSearchService) -> None:
        self.search_service = search_service

    async def search(
            self,
            query: str,
            page_number: int,
            page_size: int,
    ) -> list[Person] | None:
        search_query = self.search_service.create_query().search_persons(
            query=query,
            page_number=page_number,
            page_size=page_size,
        )
        result = await self.search_service.search(query=search_query)

        if result is None:
            return []

        return [Person(**data) for data in result]

    async def get_by_id(
            self,
            id: uuid.UUID,
    ) -> Person | None:
        get_query = self.search_service.create_query().get_person(person_id=id)
        data = await self.search_service.get(query=get_query)

        if not data:
            return None

        return Person(**data)


async def get_person_service(search_service: SearchServiceDep) -> PersonService:
    return PersonService(search_service=search_service)


PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]

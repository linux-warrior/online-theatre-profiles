from __future__ import annotations

import uuid
from enum import Enum
from http import HTTPStatus
from typing import Annotated

from fastapi import (
    Path,
    APIRouter,
    HTTPException,
)

from ..dependencies import PageDep
from ..models.films import FilmInfo, Film
from ....services import FilmServiceDep
from ....services.auth import AuthUserDep

router = APIRouter()


class SortOrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


@router.get(
    '/',
    response_model=list[Film],
    summary='Get list of films',
    description=(
            'Get list of films with sorting, pagination and filter by concrete genre. '
            'The maximum count of films on one page are 150.'
    )
)
async def get_list(
        *,
        sort: str = '',
        genre: uuid.UUID | None = None,
        page: PageDep,
        film_service: FilmServiceDep,
        _user: AuthUserDep,
) -> list[Film]:
    sort_by = {}
    if sort:
        is_first_dash = sort[0] == '-'

        field = sort[1:] if is_first_dash else sort
        sort = SortOrderEnum.desc if is_first_dash else SortOrderEnum.asc

        if field == 'imdb_rating':
            sort_by = {'field': 'rating', 'order': sort}

    if not sort_by:
        sort_by = {'field': 'id', 'order': SortOrderEnum.asc}

    film_list = await film_service.get_list(
        sort=sort_by,
        genre_uuid=genre,
        page_number=page.number,
        page_size=page.size
    )
    if not film_list:
        return []

    return [Film(**item.model_dump(by_alias=True)) for item in film_list]


@router.get(
    '/{uuid}',
    response_model=FilmInfo,
    summary='Get film by uuid',
    description='Get concrete film by uuid.'
)
async def get_by_id(
        *,
        film_uuid: Annotated[uuid.UUID, Path(alias='uuid')],
        film_service: FilmServiceDep,
        _user: AuthUserDep,
) -> FilmInfo:
    film = await film_service.get_by_id(film_uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')

    return FilmInfo(**film.model_dump(by_alias=True))


@router.get(
    '/search/',
    response_model=list[Film],
    summary='Search film by query',
    description='Search film by title with pagination. The maximum count of films on one page are 150.'
)
async def search(
        *,
        query: str = '',
        page: PageDep,
        film_service: FilmServiceDep,
        _user: AuthUserDep,
) -> list[Film]:
    if not query:
        return []

    film_list = await film_service.search(query=query, page_number=page.number, page_size=page.size)
    if not film_list:
        return []

    return [Film(**item.model_dump(by_alias=True)) for item in film_list]

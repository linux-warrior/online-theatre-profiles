from __future__ import annotations

import enum
import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import (
    Path,
    APIRouter,
    HTTPException,
)

from ..dependencies import PageParamsDep
from ..models import (
    FilmResponse,
    ExtendedFilmResponse,
    FilmRatingResponse,
    FilmReviewsResponse,
)
from ....services import FilmServiceDep
from ....services.auth import CurrentUserDep
from ....services.profiles import ProfilesServiceDep

router = APIRouter()


class SortOrderEnum(enum.StrEnum):
    ASC = 'asc'
    DESC = 'desc'


@router.get(
    '/',
    response_model=list[FilmResponse],
    summary='Get a list of films',
    description='Get a list of films with sorting, pagination and filtering by concrete genre.',
)
async def get_films_list(*,
                         sort: str = '',
                         genre: uuid.UUID | None = None,
                         page_params: PageParamsDep,
                         film_service: FilmServiceDep,
                         _current_user: CurrentUserDep) -> list[FilmResponse]:
    sort_by = {}

    if sort:
        is_first_dash = (sort[0] == '-')

        field = sort[1:] if is_first_dash else sort
        sort = SortOrderEnum.DESC if is_first_dash else SortOrderEnum.ASC

        if field == 'imdb_rating':
            sort_by = {'field': 'rating', 'order': sort}

    if not sort_by:
        sort_by = {'field': 'id', 'order': SortOrderEnum.ASC}

    films_list = await film_service.get_list(
        sort=sort_by,
        genre_uuid=genre,
        page_number=page_params.number,
        page_size=page_params.size,
    )

    return [
        FilmResponse.model_validate(film, from_attributes=True)
        for film in films_list
    ]


@router.get(
    '/{uuid}',
    response_model=ExtendedFilmResponse,
    summary='Get a film by UUID',
    description='Get a concrete film by UUID.',
)
async def get_film_by_id(*,
                         film_id: Annotated[uuid.UUID, Path(alias='uuid')],
                         film_service: FilmServiceDep,
                         profiles_service: ProfilesServiceDep,
                         _current_user: CurrentUserDep) -> ExtendedFilmResponse:
    film = await film_service.get_by_id(film_id)

    if film is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Film not found',
        )

    extended_film_response = ExtendedFilmResponse.model_validate(film, from_attributes=True)
    film_users_response = extended_film_response.users

    film_rating = await profiles_service.get_film_rating(film_id=film_id)

    if film_rating is not None:
        film_users_response.rating = FilmRatingResponse.model_validate(
            film_rating,
            from_attributes=True,
        )

    film_reviews = await profiles_service.get_film_reviews(film_id=film_id)

    if film_reviews is not None:
        film_users_response.reviews = FilmReviewsResponse.model_validate(
            film_reviews,
            from_attributes=True,
        )

    return extended_film_response


@router.get(
    '/search/',
    response_model=list[FilmResponse],
    summary='Search a film by query',
    description='Search a film by title with pagination.',
)
async def search_films(*,
                       query: str = '',
                       page_params: PageParamsDep,
                       film_service: FilmServiceDep,
                       _current_user: CurrentUserDep) -> list[FilmResponse]:
    if not query:
        return []

    films_list = await film_service.search(
        query=query,
        page_number=page_params.number,
        page_size=page_params.size,
    )

    return [
        FilmResponse.model_validate(film, from_attributes=True)
        for film in films_list
    ]

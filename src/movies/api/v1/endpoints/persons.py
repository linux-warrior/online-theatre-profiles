from __future__ import annotations

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
    PersonResponse,
    FilmResponse,
)
from ....services import (
    PersonServiceDep,
    FilmServiceDep,
)
from ....services.auth import CurrentUserDep

router = APIRouter()


@router.get(
    '/{uuid}',
    response_model=PersonResponse,
    summary='Get a person by UUID',
    description='Get a concrete person by UUID with their films and roles.',
)
async def get_person_by_id(*,
                           person_id: Annotated[uuid.UUID, Path(alias='uuid')],
                           person_service: PersonServiceDep,
                           _current_user: CurrentUserDep) -> PersonResponse:
    person = await person_service.get_by_id(person_id)

    if person is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Person not found',
        )

    return PersonResponse.model_validate(person, from_attributes=True)


@router.get(
    '/{uuid}/film/',
    response_model=list[FilmResponse],
    summary='Get a list of films by person UUID',
    description='Get a list of person films with their IMDB rating.',
)
async def get_person_films(*,
                           person_id: Annotated[uuid.UUID, Path(alias='uuid')],
                           film_service: FilmServiceDep,
                           _current_user: CurrentUserDep) -> list[FilmResponse]:
    films_list = await film_service.get_list_by_person(person_id)

    return [
        FilmResponse.model_validate(film, from_attributes=True)
        for film in films_list
    ]


@router.get(
    '/search/',
    response_model=list[PersonResponse],
    summary='Search a person',
    description='Search a person with their films and roles by full name with pagination.',
)
async def search(*,
                 query: str = '',
                 page_params: PageParamsDep,
                 person_service: PersonServiceDep,
                 _current_user: CurrentUserDep) -> list[PersonResponse]:
    if not query:
        return []

    persons_list = await person_service.search(
        query=query,
        page_number=page_params.number,
        page_size=page_params.size,
    )

    return [
        PersonResponse.model_validate(person, from_attributes=True)
        for person in persons_list
    ]

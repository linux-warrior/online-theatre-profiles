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
from ..models import GenreResponse
from ....services import GenreServiceDep
from ....services.auth import CurrentUserDep

router = APIRouter()


@router.get(
    '/',
    response_model=list[GenreResponse],
    summary='Get a list of genres',
    description='Get list a of genres with pagination.',
)
async def get_genres_list(*,
                          page_params: PageParamsDep,
                          genre_service: GenreServiceDep,
                          _current_user: CurrentUserDep) -> list[GenreResponse]:
    genres_list = await genre_service.get_list(
        page_number=page_params.number,
        page_size=page_params.size,
    )

    return [
        GenreResponse.model_validate(genre, from_attributes=True)
        for genre in genres_list
    ]


@router.get(
    '/{uuid}',
    response_model=GenreResponse,
    summary='Get a genre by UUID',
    description='Get a concrete genre by UUID.',
)
async def get_genre_by_id(*,
                          genre_id: Annotated[uuid.UUID, Path(alias='uuid')],
                          genre_service: GenreServiceDep,
                          _current_user: CurrentUserDep) -> GenreResponse:
    genre = await genre_service.get_by_id(genre_id)

    if genre is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genre not found',
        )

    return GenreResponse.model_validate(genre, from_attributes=True)

from __future__ import annotations

from fastapi import (
    Response,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .base import Transport


class BearerResponse(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str


class BearerTransport(Transport):
    async def get_login_response(self, access_token: str, refresh_token: str) -> Response:
        return await self._create_bearer_response(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def get_logout_response(self) -> Response:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def get_refresh_response(self, access_token: str, refresh_token: str) -> Response:
        return await self._create_bearer_response(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def _create_bearer_response(self, access_token: str, refresh_token: str) -> Response:
        bearer_response = BearerResponse(
            token_type='bearer',
            access_token=access_token,
            refresh_token=refresh_token,
        )
        return JSONResponse(bearer_response.model_dump())

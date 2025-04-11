from __future__ import annotations

import uuid
from urllib.parse import urljoin

import http
import pytest

from ...settings import settings


@pytest.mark.asyncio(loop_scope='session')
async def test_openapi(aiohttp_session) -> None:
    openapi_url = urljoin(settings.movies_api_url, 'openapi.json')

    headers = {
        'X-Request-Id': str(uuid.uuid4())
    }

    async with aiohttp_session.get(openapi_url, headers=headers) as response:
        assert response.status == http.HTTPStatus.OK
        response_data: dict = await response.json()

    assert set(response_data) == {
        'openapi',
        'info',
        'paths',
        'components',
    }
    assert response_data['info']['title'] == 'movies'

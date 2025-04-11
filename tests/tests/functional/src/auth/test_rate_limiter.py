from __future__ import annotations

import http
from urllib.parse import urljoin

import pytest

from ...settings import settings


@pytest.mark.skip
@pytest.mark.asyncio(loop_scope='session')
async def test_rate_limiter(aiohttp_session) -> None:
    register_data = {
        'login': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'register/')
    await aiohttp_session.post(url, json=register_data)

    login_data = {
        'grant_type': 'password',
        'username': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    for i in range(settings.ratelimiter.times + 1):
        await aiohttp_session.post(url, data=login_data)
    async with aiohttp_session.post(url, data=login_data) as response:
        status = response.status
    assert status == http.HTTPStatus.TOO_MANY_REQUESTS

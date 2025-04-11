from __future__ import annotations

import http
from urllib.parse import urljoin

import pytest

from ...settings import settings


@pytest.mark.parametrize(
    "input_data, expected_data",
    [
        (
                {
                    'login': 'test_user',
                    'password': '123456',
                },
                {
                    'count_login': 1,
                },
        ),
    ],
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_login_history(
        aiohttp_session,
        clean_all_tables_before,
        input_data,
        expected_data,
):
    user_create_data = {
        'login': input_data['login'],
        'password': input_data['password'],
    }
    register_url = urljoin(settings.auth_api_v1_url, 'register')

    async with aiohttp_session.post(register_url, json=user_create_data) as register_response:
        assert register_response.status == http.HTTPStatus.CREATED

    user_login_data = {
        'grant_type': 'password',
        'username': user_create_data['login'],
        'password': user_create_data['password'],
    }
    login_url = urljoin(settings.auth_api_v1_url, 'jwt/login')

    async with aiohttp_session.post(login_url, data=user_login_data) as login_response:
        assert login_response.status == http.HTTPStatus.OK
        login_response_data = await login_response.json()

    token_jwt = login_response_data['access_token']
    token_type = login_response_data['token_type']

    headers = {
        'Accept': 'application/json',
        'Authorization': f'{token_type.title()} {token_jwt}',
    }
    login_history_url = urljoin(settings.auth_api_v1_url, 'users/get_login_history')

    async with aiohttp_session.get(login_history_url, headers=headers) as login_history_response:
        assert login_history_response.status == http.HTTPStatus.OK
        history_response_data = await login_history_response.json()

    assert len(history_response_data) == expected_data['count_login']

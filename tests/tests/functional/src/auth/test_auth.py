from __future__ import annotations

import http
from urllib.parse import urljoin

import pytest

from ...settings import settings


@pytest.mark.asyncio(loop_scope='session')
async def test_register(aiohttp_session, clean_all_tables_before) -> None:
    register_data = {
        'login': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'register/')

    async with aiohttp_session.post(url, json=register_data) as response:
        status = response.status
        assert status == http.HTTPStatus.CREATED


@pytest.mark.asyncio(loop_scope='session')
async def test_register_user_exists(aiohttp_session) -> None:
    register_data = {
        'login': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'register/')

    await aiohttp_session.post(url, json=register_data)
    async with aiohttp_session.post(url, json=register_data) as response:
        status = response.status
        data = await response.json()

    assert status == http.HTTPStatus.BAD_REQUEST
    assert data['detail'] == 'REGISTER_USER_ALREADY_EXISTS'


@pytest.mark.parametrize(
    'login_data, expected_data',
    [
        (
                {
                    'grant_type': 'password',
                    'username': 'test_user',
                    'password': 'password',
                },
                {'status': http.HTTPStatus.OK},
        ),
        (
                {
                    'grant_type': 'password',
                    'username': 'test_user_BAD_CREDENTIALS',
                    'password': 'password',
                },
                {'status': http.HTTPStatus.BAD_REQUEST, 'detail': 'LOGIN_BAD_CREDENTIALS'},
        ),
    ],
)
@pytest.mark.asyncio(loop_scope='session')
async def test_login(aiohttp_session, login_data, expected_data) -> None:
    register_data = {
        'login': 'test_user',
        'password': 'password',
    }

    url = urljoin(settings.auth_api_v1_url, 'register/')
    await aiohttp_session.post(url, json=register_data)

    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')

    async with aiohttp_session.post(url, data=login_data) as response:
        status = response.status
        assert status == expected_data['status']

        data = await response.json()
        if expected_data['status'] == http.HTTPStatus.BAD_REQUEST:
            assert data['detail'] == expected_data['detail']


@pytest.mark.asyncio(loop_scope='session')
async def test_refresh(aiohttp_session) -> None:
    login_url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    login_data = {
        'grant_type': 'password',
        'username': 'test_user',
        'password': 'password',
    }

    async with aiohttp_session.post(login_url, data=login_data) as response:
        assert response.status == http.HTTPStatus.OK
        response_data = await response.json()

    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']

    refresh_url = urljoin(settings.auth_api_v1_url, 'jwt/refresh/')
    refresh_data = {
        'refresh_token': refresh_token,
    }

    async with aiohttp_session.post(refresh_url, data=refresh_data) as response:
        assert response.status == http.HTTPStatus.OK
        response_data = await response.json()

    assert response_data['access_token'] != access_token
    assert response_data['refresh_token'] != refresh_token

    async with aiohttp_session.post(refresh_url, data=refresh_data) as response:
        assert response.status == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope='session')
async def test_get_current_user(aiohttp_session) -> None:
    login_data = {
        'grant_type': 'password',
        'username': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')

    async with aiohttp_session.post(url, data=login_data) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()

    token_jwt = data['access_token']
    token_type = data['token_type']
    headers = {
        'accept': 'application/json',
        'Authorization': f'{token_type.title()} {token_jwt}'
    }
    url = urljoin(settings.auth_api_v1_url, 'users/me/')

    async with aiohttp_session.get(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()
        assert data['login'] == login_data['username']


@pytest.mark.asyncio(loop_scope='session')
async def test_patch_current_user(aiohttp_session, clean_all_tables_after) -> None:
    login_data = {
        'grant_type': 'password',
        'username': 'test_user',
        'password': 'password',
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')

    async with aiohttp_session.post(url, data=login_data) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()

    token_jwt = data['access_token']
    token_type = data['token_type']
    headers = {
        'accept': 'application/json',
        'Authorization': f'{token_type.title()} {token_jwt}',
        'Content-Type': 'application/json',
    }
    url = urljoin(settings.auth_api_v1_url, 'users/me/')

    async with aiohttp_session.get(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.OK

    patch_data = {
        'login': 'test_user2',
        'password': 'password',
        'is_superuser': False,
    }

    async with aiohttp_session.patch(url, headers=headers, json=patch_data) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()
        assert data['login'] == patch_data['login']


@pytest.mark.asyncio(loop_scope='session')
async def test_logout(aiohttp_session) -> None:
    login_url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    login_data = {
        'grant_type': 'password',
        'username': 'test_user2',
        'password': 'password',
    }

    async with aiohttp_session.post(login_url, data=login_data) as response:
        assert response.status == http.HTTPStatus.OK
        response_data = await response.json()

    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    token_type = response_data['token_type']
    headers = {
        'accept': 'application/json',
        'Authorization': f'{token_type.title()} {access_token}',
    }

    logout_url = urljoin(settings.auth_api_v1_url, 'jwt/logout/')

    async with aiohttp_session.post(logout_url, headers=headers) as response:
        assert response.status == http.HTTPStatus.NO_CONTENT

    async with aiohttp_session.post(logout_url, headers=headers) as response:
        assert response.status == http.HTTPStatus.UNAUTHORIZED

    refresh_url = urljoin(settings.auth_api_v1_url, 'jwt/refresh/')
    refresh_data = {
        'refresh_token': refresh_token,
    }

    async with aiohttp_session.post(refresh_url, data=refresh_data) as response:
        assert response.status == http.HTTPStatus.UNAUTHORIZED

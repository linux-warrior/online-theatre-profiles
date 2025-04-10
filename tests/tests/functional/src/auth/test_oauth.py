from __future__ import annotations

import http
from urllib.parse import urljoin, urlparse, parse_qs

import pytest

from ...settings import settings


@pytest.mark.asyncio(loop_scope='session')
async def test_oauth_success(aiohttp_session, clean_all_tables_before) -> None:
    authorize_url = urljoin(settings.auth_api_v1_url, 'oauth/google/authorize/')

    async with aiohttp_session.get(authorize_url) as response:
        assert response.status == http.HTTPStatus.OK
        response_data = await response.json()

    assert set(response_data) == {'authorization_url'}

    authorization_url = response_data['authorization_url']
    authorization_url_obj = urlparse(authorization_url)
    authorization_query_data = parse_qs(authorization_url_obj.query)

    assert set(authorization_query_data) == {
        'response_type',
        'client_id',
        'redirect_uri',
        'state',
        'scope',
    }
    assert authorization_query_data['response_type'][0] == 'code'
    assert authorization_query_data['client_id'][0] == 'client_id'
    assert authorization_query_data['redirect_uri'][0] == urljoin(
        settings.auth_api_v1_url,
        'oauth/google/callback',
    )
    assert authorization_query_data['scope'][0] == (
        'https://www.googleapis.com/auth/userinfo.profile '
        'https://www.googleapis.com/auth/userinfo.email'
    )

    state = authorization_query_data['state'][0]
    callback_url = urljoin(settings.auth_api_v1_url, 'oauth/google/callback/')

    async with aiohttp_session.get(callback_url, params={
        'code': 'test',
        'code_verifier': 'test',
        'state': state,
    }) as response:
        assert response.status == http.HTTPStatus.OK
        response_data = await response.json()

    assert set(response_data) == {
        'token_type',
        'access_token',
        'refresh_token',
    }
    assert response_data['token_type'] == 'bearer'

    access_token = response_data['access_token']
    profile_url = urljoin(settings.auth_api_v1_url, 'users/me/')

    async with aiohttp_session.get(profile_url, headers={
        'Authorization': f'Bearer {access_token}',
    }) as response:
        assert response.status == http.HTTPStatus.OK
        response_data = await response.json()

    assert set(response_data) >= {
        'id',
        'login',
        'email',
        'is_superuser',
    }
    assert response_data['login'] is None
    assert response_data['email'] == 'user@gmail.com'
    assert response_data['is_superuser'] is False

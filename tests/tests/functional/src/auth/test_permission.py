from __future__ import annotations

import pytest
from urllib.parse import urljoin
import http


from ...settings import settings
user_id_save = {}
role_id_save = {}
user_role_id_save = {}

@pytest.mark.parametrize(
    'user, role, expected',
    [
        (
            {
            'login': 'test_user',
            'password': 'password',
            'is_superuser': False
            },
            {
            'name': 'string',
            'code': 'admin'
            },
            http.HTTPStatus.CREATED
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_permision_assign(
    aiohttp_session, auth_headers, clean_all_tables_before, user, role, expected):
    url = urljoin(settings.auth_api_v1_url, 'register/')
    async with aiohttp_session.post(url, json=user) as response:
        status = response.status
        assert status == expected
        data = await response.json()
        user_id_save['id'] = data['id']
    headers = auth_headers
    url = urljoin(settings.auth_api_v1_url, 'roles/create/')
    async with aiohttp_session.post(url, headers=headers, json=role) as response:
        status = response.status
        assert status == expected
        data = await response.json()
        role_id_save['id'] = data['id']
    input_data = {
        'user_id': user_id_save.get('id'),
        'role_id': role_id_save.get('id')
    }
    url = urljoin(settings.auth_api_v1_url, 'permissions/assign/')
    async with aiohttp_session.post(url, headers=headers, json=input_data) as response:
        status = response.status
        data = await response.json()
        user_role_id_save['id'] = data['id']
        assert status == expected

@pytest.mark.asyncio(loop_scope='session')
async def test_permision_get_by_user(
    aiohttp_session, auth_headers):
    headers = auth_headers
    url = urljoin(settings.auth_api_v1_url, f'permissions/get_by_user/{user_id_save.get('id')}')
    async with aiohttp_session.get(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()
        assert data[0]['role_id'] == role_id_save.get('id')

@pytest.mark.asyncio(loop_scope='session')
async def test_permision_revoke(
    aiohttp_session, auth_headers, clean_all_tables_after):
    headers = auth_headers
    url = urljoin(settings.auth_api_v1_url, f'permissions/revoke/{user_role_id_save.get('id')}')
    async with aiohttp_session.delete(url, headers=headers) as response:
        status = response.status
        assert status == http.HTTPStatus.OK
        data = await response.json()
        assert data['id'] == user_role_id_save.get('id')
        assert data['role_id'] == role_id_save.get('id')

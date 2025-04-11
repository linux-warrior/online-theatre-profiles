import uuid
from urllib.parse import urljoin
import http

import pytest

from ...settings import settings
from ...utils.elasticsearch.models import (
    Film,
    Person,
)

INDEX_NAME_FILM = 'films'
INDEX_NAME_PERSON = 'persons'


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {'search': 'Star'},
            {'status': http.HTTPStatus.OK, 'length': 1}
        ),
        (
            {'search': 'Mashed potato'},
            {'status': http.HTTPStatus.OK, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search_film(
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
        input,
        expected
):
    film = Film(
        title='The Star',
        description='Description',
        rating=6.7,
    )

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_FILM)
    await elastic.load_documents(documents=[film])

    url = urljoin(settings.movies_api_v1_url, 'films/search/')
    async with aiohttp_session.get(
            url,
            headers=auth_headers,
            params={'query': input['search']}
    ) as response:
        status = response.status
        data = await response.json()

        assert status == expected['status']
        assert len(data) == expected['length']


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'person_full_name': 'Jeffry Jones',
                'search_full_name': 'jones'
            },
            {'status': http.HTTPStatus.OK, 'length': 1, 'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429'}
        ),
        (
            {
                'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'person_full_name': 'Jeffry Jones',
                'search_full_name': 'Julie Pi'
            },
            {'status': http.HTTPStatus.OK, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search_person(
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
        input,
        expected
):
    persons = [
        Person(
            id=uuid.UUID(input['person_uuid']),
            full_name=input['person_full_name']
        ),
        Person(
            full_name='Josse Sue'
        ),
    ]

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_PERSON)
    await elastic.load_documents(documents=persons)

    url = urljoin(settings.movies_api_v1_url, 'persons/search/')
    async with aiohttp_session.get(
            url,
            headers=auth_headers,
            params={'query': input['search_full_name']}
    ) as response:
        status = response.status
        data = await response.json()

        assert status == expected['status']
        assert len(data) == expected['length']

        if 'person_uuid' in expected:
            assert data[0]['uuid'] == expected['person_uuid']


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429',
                'person_full_name': 'Jeffry Jones',
                'search_full_name': 'jones'
            },
            {'status': http.HTTPStatus.OK, 'length': 1, 'person_uuid': 'e9c1dfa4-cfbf-40b8-b636-9075c2fd8429'}
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search_person_with_redis(
        create_elasticsearch_index,
        aiohttp_session,
        auth_headers,
        input,
        expected
):
    person = Person(
        id=uuid.UUID(input['person_uuid']),
        full_name=input['person_full_name']
    )

    elastic = await create_elasticsearch_index(index_name=INDEX_NAME_PERSON)
    await elastic.load_documents(documents=[person])

    async def inner_test_search_person_with_redis(aiohttp_session, input, expected):
        url = urljoin(settings.movies_api_v1_url, 'persons/search/')
        async with aiohttp_session.get(
                url,
                headers=auth_headers,
                params={'query': input['search_full_name']}
        ) as response:
            status = response.status
            data = await response.json()

            assert status == expected['status']
            assert len(data) == expected['length']

            if 'person_uuid' in expected:
                assert data[0]['uuid'] == expected['person_uuid']

    await inner_test_search_person_with_redis(aiohttp_session, input, expected)

    await elastic.delete_index()

    await inner_test_search_person_with_redis(aiohttp_session, input, expected)

from __future__ import annotations

import uuid
from urllib.parse import urljoin

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from ..settings import settings

auth = settings.auth_postgresql
DATABASE_URL = f'postgresql+asyncpg://{auth.username}:{auth.password}@{auth.host}:{auth.port}/{auth.database}'
TABLES = ['login_history', 'user_role', 'user', 'role']


@pytest_asyncio.fixture(scope='session')
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope='module')
async def async_session(async_engine):
    async_session_maker = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope='module')
async def clean_all_tables(async_session):
    for table in TABLES:
        await async_session.execute(
            text(f'TRUNCATE TABLE auth.{table} RESTART IDENTITY CASCADE')
        )
    await async_session.commit()


@pytest_asyncio.fixture(scope='module')
async def clean_all_tables_before(async_session):
    for table in TABLES:
        if table == 'user':
            query = f'DELETE FROM auth.user WHERE is_superuser != true'
        else:
            query = f'TRUNCATE TABLE auth.{table} RESTART IDENTITY CASCADE'
        await async_session.execute(
            text(query)
        )
    await async_session.commit()
    yield


@pytest_asyncio.fixture(scope='module')
async def clean_all_tables_after(async_session):
    yield
    for table in TABLES:
        if table == 'user':
            query = f'DELETE FROM auth.user WHERE is_superuser != true'
        else:
            query = f'TRUNCATE TABLE auth.{table} RESTART IDENTITY CASCADE'
        await async_session.execute(
            text(query)
        )
    await async_session.commit()


@pytest_asyncio.fixture(scope='module')
async def auth_headers(aiohttp_session):
    superuser = {
        'grant_type': 'password',
        'username': settings.superuser.login,
        'password': settings.superuser.password
    }
    url = urljoin(settings.auth_api_v1_url, 'jwt/login/')
    async with aiohttp_session.post(url, data=superuser) as response:
        data = await response.json()
        token_jwt = data['access_token']
        token_type = data['token_type']
        headers = {
            'accept': 'application/json',
            'Authorization': f'{token_type.title()} {token_jwt}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(uuid.uuid4())
        }
        return headers

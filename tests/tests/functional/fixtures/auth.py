from __future__ import annotations

import uuid
from collections.abc import Sequence, AsyncGenerator
from urllib.parse import urljoin

import aiohttp
import pytest_asyncio
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.sql import text

from ..settings import settings

AUTH_TABLES: Sequence[str] = [
    'login_history',
    'user_role',
    'user',
    'role',
]


@pytest_asyncio.fixture(scope='session')
async def _auth_async_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(settings.auth_postgresql.engine_url, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope='session')
async def _auth_async_session_maker(
        _auth_async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(_auth_async_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope='module')
async def _auth_async_session(
        _auth_async_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with _auth_async_session_maker() as session:
        yield session
        await session.rollback()


async def _clean_all_tables(*, session: AsyncSession) -> None:
    for table in AUTH_TABLES:
        if table == 'user':
            query = f'DELETE FROM auth.user WHERE auth.user.is_superuser IS NOT TRUE'
        else:
            query = f'TRUNCATE TABLE auth.{table} RESTART IDENTITY CASCADE'

        await session.execute(text(query))

    await session.commit()


@pytest_asyncio.fixture(scope='module')
async def auth_clean_all_tables_before(_auth_async_session: AsyncSession) -> None:
    await _clean_all_tables(session=_auth_async_session)


@pytest_asyncio.fixture(scope='module')
async def auth_clean_all_tables_after(
        _auth_async_session: AsyncSession,
) -> AsyncGenerator[None]:
    yield
    await _clean_all_tables(session=_auth_async_session)


@pytest_asyncio.fixture(scope='module')
async def auth_headers(aiohttp_session: aiohttp.ClientSession) -> dict:
    login_data = {
        'grant_type': 'password',
        'username': settings.auth_superuser.login,
        'password': settings.auth_superuser.password,
    }
    login_url = urljoin(settings.auth_api_v1_url, 'jwt/login/')

    async with aiohttp_session.post(login_url, data=login_data) as response:
        response_data = await response.json()

    token_jwt = response_data['access_token']
    token_type = response_data['token_type']

    return {
        'accept': 'application/json',
        'Authorization': f'{token_type.title()} {token_jwt}',
        'X-Request-Id': str(uuid.uuid4()),
    }


@pytest_asyncio.fixture(scope='session')
async def _auth_redis_client() -> AsyncGenerator[redis.Redis]:
    async with (
        redis.Redis(
            host=settings.auth_redis.host,
            port=settings.auth_redis.port,
        ) as auth_redis_client,
    ):
        yield auth_redis_client


@pytest_asyncio.fixture(scope='function', autouse=True)
async def _auth_reset_rate_limit(_auth_redis_client: redis.Redis) -> None:
    await _auth_redis_client.flushdb()

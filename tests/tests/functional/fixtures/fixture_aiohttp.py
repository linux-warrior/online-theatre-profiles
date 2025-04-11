import aiohttp
from collections.abc import AsyncGenerator
import pytest_asyncio


@pytest_asyncio.fixture(scope='session')
async def aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session
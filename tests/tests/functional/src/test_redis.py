from __future__ import annotations

import pytest


@pytest.mark.asyncio(loop_scope='session')
async def test_redis_cache(clear_redis_cache) -> None:
    await clear_redis_cache()

from __future__ import annotations

import abc
import uuid
from typing import Any

from .exceptions import InvalidToken
from .....cache import (
    AbstractCache,
)


class AbstractTokenProcessor(abc.ABC):
    @abc.abstractmethod
    async def validate_token(self, *, token_id: uuid.UUID) -> None: ...

    @abc.abstractmethod
    async def save_token(self, *, token_id: uuid.UUID) -> None: ...

    @abc.abstractmethod
    async def destroy_token(self, *, token_id: uuid.UUID) -> None: ...


class BaseTokenProcessor(AbstractTokenProcessor):
    cache: AbstractCache

    def __init__(self, *, cache: AbstractCache) -> None:
        self.cache = cache

    async def validate_token(self, *, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id=token_id)

        if not await self._is_cache_valid(cache_key=cache_key):
            raise InvalidToken

    @abc.abstractmethod
    def _create_cache_key(self, *, token_id: uuid.UUID) -> str: ...

    @abc.abstractmethod
    async def _is_cache_valid(self, *, cache_key: str) -> bool: ...

    async def save_token(self, *, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id=token_id)
        await self._save_cache(cache_key=cache_key)

    @abc.abstractmethod
    async def _save_cache(self, *, cache_key: str) -> None: ...

    async def destroy_token(self, *, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id=token_id)
        await self._delete_cache(cache_key=cache_key)

    @abc.abstractmethod
    async def _delete_cache(self, *, cache_key: str) -> None: ...


class AccessTokenProcessor(BaseTokenProcessor):
    lifetime: int | None

    def __init__(self, *, lifetime: int | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.lifetime = lifetime

    def _create_cache_key(self, token_id: uuid.UUID) -> str:
        return f'access-{token_id}'

    async def _is_cache_valid(self, *, cache_key: str) -> bool:
        return await self.cache.get(cache_key) is None

    async def _save_cache(self, *, cache_key: str) -> None:
        pass

    async def _delete_cache(self, *, cache_key: str) -> None:
        await self.cache.set(cache_key, 'access', timeout=self.lifetime)


class RefreshTokenProcessor(BaseTokenProcessor):
    lifetime: int | None

    def __init__(self, *, lifetime: int | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.lifetime = lifetime

    def _create_cache_key(self, token_id: uuid.UUID) -> str:
        return f'refresh-{token_id}'

    async def _is_cache_valid(self, *, cache_key: str) -> bool:
        return await self.cache.get(cache_key) is not None

    async def _save_cache(self, *, cache_key: str) -> None:
        await self.cache.set(cache_key, 'refresh', timeout=self.lifetime)

    async def _delete_cache(self, *, cache_key: str) -> None:
        await self.cache.delete(cache_key)

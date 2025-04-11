from __future__ import annotations

import abc
import hashlib
import json

from .backends import AbstractCache


class Parameterizable(abc.ABC):
    @abc.abstractmethod
    def get_cache_prefix(self) -> str: ...

    @abc.abstractmethod
    def get_cache_params(self) -> dict: ...


class ParameterizedCache[TParams: Parameterizable, TValue]:
    cache: AbstractCache

    def __init__(self, *, cache: AbstractCache) -> None:
        self.cache = cache

    async def get(self, *, params: TParams) -> TValue | None:
        cache_key = self._create_cache_key(params=params)
        value_json: str | None = await self.cache.get(cache_key)

        if value_json is None:
            return None

        return json.loads(value_json)

    async def set(self, *, params: TParams, value: TValue) -> None:
        cache_key = self._create_cache_key(params=params)
        value_json = json.dumps(value)

        await self.cache.set(cache_key, value_json)

    def _create_cache_key(self, *, params: TParams) -> str:
        cache_prefix = params.get_cache_prefix()
        cache_params = params.get_cache_params()

        key_dict = {
            'params': cache_params,
        }
        key_json = json.dumps(key_dict, sort_keys=True)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()

        return f'{cache_prefix}-{key_hash}'

from __future__ import annotations

import abc

from .cache import AbstractCache


class AbstractCacheService(abc.ABC):
    @abc.abstractmethod
    def get_cache(self,
                  *,
                  key_prefix: str | None = None,
                  key_version: str | None = None) -> AbstractCache: ...

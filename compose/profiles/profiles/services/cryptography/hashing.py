from __future__ import annotations

import abc

from cryptography.hazmat.primitives import hashes, hmac

from ...core.config import settings


class AbstractHashingTool(abc.ABC):
    @abc.abstractmethod
    def salted_hmac(self, value: str | None) -> str | None: ...


class HashingTool(AbstractHashingTool):
    _secret_key: str
    _salt: str

    def __init__(self, *, salt: str | None = None) -> None:
        self._secret_key = settings.profiles.secret_key
        self._salt = salt or 'profiles.services.cryptography.hashing.HashingTool'

    def salted_hmac(self, value: str | None) -> str | None:
        if value is None:
            return None

        hmac_obj = hmac.HMAC(self._secret_key.encode(), hashes.SHA256())
        hmac_obj.update(f'{self._salt}:{value}'.encode())
        hmac_bytes = hmac_obj.finalize()

        return hmac_bytes.hex()

from __future__ import annotations

import abc

from cryptography.hazmat.primitives import hashes, hmac

from ...core.config import settings


class AbstractHashingTool(abc.ABC):
    @abc.abstractmethod
    def salted_hmac(self, value: str | None) -> str | None: ...


class HashingTool(AbstractHashingTool):
    secret_key: str
    salt: str

    def __init__(self, *, salt: str | None = None) -> None:
        self.secret_key = settings.profiles.secret_key
        self.salt = salt or 'profiles.services.cryptography.hashing.HashingTool'

    def salted_hmac(self, value: str | None) -> str | None:
        if value is None:
            return None

        hmac_obj = hmac.HMAC(self.secret_key.encode(), hashes.SHA256())
        hmac_obj.update(f'{self.salt}:{value}'.encode())
        hmac_bytes = hmac_obj.finalize()

        return hmac_bytes.hex()

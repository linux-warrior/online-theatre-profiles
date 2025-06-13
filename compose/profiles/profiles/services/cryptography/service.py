from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import Annotated, Any

from cryptography.fernet import Fernet, InvalidToken
from fastapi import Depends

from ...core.config import settings


class AbstractEncryptionService(abc.ABC):
    @abc.abstractmethod
    def encrypt(self, value: str | None) -> str | None: ...

    @abc.abstractmethod
    def encrypt_dict(self, data: dict[str, Any], keys: Iterable[str] | None = None) -> dict[str, Any]: ...

    @abc.abstractmethod
    def decrypt(self, value: str | None) -> str | None: ...

    @abc.abstractmethod
    def decrypt_dict(self, data: dict[str, Any], keys: Iterable[str] | None = None) -> dict[str, Any]: ...


class EncryptionService(AbstractEncryptionService):
    fernet: Fernet

    def __init__(self) -> None:
        self.fernet = Fernet(settings.profiles.encryption_key)

    def encrypt(self, value: str | None) -> str | None:
        if value is None:
            return None

        return self.fernet.encrypt(value.encode()).decode()

    def encrypt_dict(self, data: dict[str, Any], keys: Iterable[str] | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {**data}
        keys = keys or []

        for key in keys:
            try:
                value = result[key]
            except KeyError:
                continue

            result[key] = self.encrypt(value)

        return result

    def decrypt(self, value: str | None) -> str | None:
        if value is None:
            return None

        try:
            return self.fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            return value

    def decrypt_dict(self, data: dict[str, Any], keys: Iterable[str] | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {**data}
        keys = keys or []

        for key in keys:
            try:
                value = result[key]
            except KeyError:
                continue

            result[key] = self.decrypt(value)

        return result


async def get_encryption_service() -> AbstractEncryptionService:
    return EncryptionService()


EncryptionServiceDep = Annotated[EncryptionService, Depends(get_encryption_service)]

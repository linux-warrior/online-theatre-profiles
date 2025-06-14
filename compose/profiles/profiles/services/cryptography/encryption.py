from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from .hashing import (
    AbstractHashingTool,
)
from ...core.config import settings


class AbstractEncryptionTool(abc.ABC):
    @abc.abstractmethod
    def encrypt(self, value: str | None) -> str | None: ...

    @abc.abstractmethod
    def decrypt(self, value: str | None) -> str | None: ...


class EncryptionTool(AbstractEncryptionTool):
    fernet: Fernet

    def __init__(self) -> None:
        self.fernet = Fernet(settings.profiles.encryption_key)

    def encrypt(self, value: str | None) -> str | None:
        if value is None:
            return None

        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str | None) -> str | None:
        if value is None:
            return None

        try:
            return self.fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            return value


class AbstractDictEncryptionTool(abc.ABC):
    @abc.abstractmethod
    def encrypt(self, data: dict[str, Any]) -> dict[str, Any]: ...

    @abc.abstractmethod
    def decrypt(self, data: dict[str, Any]) -> dict[str, Any]: ...


class DictEncryptionTool(AbstractDictEncryptionTool):
    encryption_tool: AbstractEncryptionTool
    hashing_tool: AbstractHashingTool
    fields: Iterable[str]

    def __init__(self,
                 *,
                 encryption_tool: AbstractEncryptionTool,
                 hashing_tool: AbstractHashingTool,
                 fields: Iterable[str] | None = None) -> None:
        self.encryption_tool = encryption_tool
        self.hashing_tool = hashing_tool
        self.fields = fields or []

    def encrypt(self, data: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {**data}

        for field_name in self.fields:
            try:
                value = result[field_name]
            except KeyError:
                continue

            result[field_name] = self.encryption_tool.encrypt(value)
            result[f'{field_name}_hash'] = self.hashing_tool.salted_hmac(value)

        return result

    def decrypt(self, data: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {**data}

        for field_name in self.fields:
            try:
                value = result[field_name]
            except KeyError:
                continue

            result[field_name] = self.encryption_tool.decrypt(value)

        return result

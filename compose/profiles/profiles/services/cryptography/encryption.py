from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

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
    keys: Iterable[str]

    def __init__(self, *, encryption_tool: AbstractEncryptionTool, keys: Iterable[str]) -> None:
        self.encryption_tool = encryption_tool
        self.keys = keys

    def encrypt(self, data: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {**data}

        for key in self.keys:
            try:
                value = result[key]
            except KeyError:
                continue

            result[key] = self.encryption_tool.encrypt(value)

        return result

    def decrypt(self, data: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {**data}

        for key in self.keys:
            try:
                value = result[key]
            except KeyError:
                continue

            result[key] = self.encryption_tool.decrypt(value)

        return result

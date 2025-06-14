from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import Annotated

from fastapi import Depends

from .encryption import (
    AbstractEncryptionTool,
    EncryptionTool,
    AbstractDictEncryptionTool,
    DictEncryptionTool,
)


class AbstractCryptographyService(abc.ABC):
    @abc.abstractmethod
    def get_encryption_tool(self) -> AbstractEncryptionTool: ...

    @abc.abstractmethod
    def get_dict_encryption_tool(self, *, keys: Iterable[str]) -> AbstractDictEncryptionTool: ...


class CryptographyService(AbstractCryptographyService):
    def get_encryption_tool(self) -> AbstractEncryptionTool:
        return EncryptionTool()

    def get_dict_encryption_tool(self, *, keys: Iterable[str]) -> AbstractDictEncryptionTool:
        encryption_tool = self.get_encryption_tool()

        return DictEncryptionTool(
            encryption_tool=encryption_tool,
            keys=keys,
        )


async def get_cryptography_service() -> AbstractCryptographyService:
    return CryptographyService()


CryptographyServiceDep = Annotated[AbstractCryptographyService, Depends(get_cryptography_service)]

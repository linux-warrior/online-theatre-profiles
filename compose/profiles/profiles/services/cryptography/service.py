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
from .hashing import (
    AbstractHashingTool,
    HashingTool,
)


class AbstractCryptographyService(abc.ABC):
    @abc.abstractmethod
    def get_encryption_tool(self) -> AbstractEncryptionTool: ...

    @abc.abstractmethod
    def get_hashing_tool(self, *, salt: str | None = None) -> AbstractHashingTool: ...

    @abc.abstractmethod
    def get_dict_encryption_tool(self,
                                 *,
                                 fields: Iterable[str] | None = None,
                                 salt: str | None = None) -> AbstractDictEncryptionTool: ...


class CryptographyService(AbstractCryptographyService):
    def get_encryption_tool(self) -> AbstractEncryptionTool:
        return EncryptionTool()

    def get_hashing_tool(self, *, salt: str | None = None) -> AbstractHashingTool:
        return HashingTool(salt=salt)

    def get_dict_encryption_tool(self,
                                 *,
                                 fields: Iterable[str] | None = None,
                                 salt: str | None = None) -> AbstractDictEncryptionTool:
        encryption_tool = self.get_encryption_tool()
        hashing_tool = self.get_hashing_tool(salt=salt)

        return DictEncryptionTool(
            encryption_tool=encryption_tool,
            hashing_tool=hashing_tool,
            fields=fields,
        )


async def get_cryptography_service() -> AbstractCryptographyService:
    return CryptographyService()


CryptographyServiceDep = Annotated[AbstractCryptographyService, Depends(get_cryptography_service)]

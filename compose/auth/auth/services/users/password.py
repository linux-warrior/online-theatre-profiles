from __future__ import annotations

import abc
import secrets
from typing import Annotated

from fastapi import Depends
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher


class AbstractPasswordHelper(abc.ABC):
    @abc.abstractmethod
    def verify_and_update(self, *, password: str, password_hash: str) -> tuple[bool, str | None]: ...

    @abc.abstractmethod
    def hash(self, *, password: str) -> str: ...

    @abc.abstractmethod
    def generate(self) -> str: ...


class PasswordHelper(AbstractPasswordHelper):
    def __init__(self, password_hash: PasswordHash) -> None:
        self.password_hash = password_hash

    def verify_and_update(self, *, password: str, password_hash: str) -> tuple[bool, str | None]:
        return self.password_hash.verify_and_update(password, password_hash)

    def hash(self, *, password: str) -> str:
        return self.password_hash.hash(password)

    def generate(self) -> str:
        return secrets.token_urlsafe()


async def get_password_helper() -> AbstractPasswordHelper:
    return PasswordHelper(password_hash=PasswordHash([
        Argon2Hasher(),
        BcryptHasher(),
    ]))


PasswordHelperDep = Annotated[AbstractPasswordHelper, Depends(get_password_helper)]

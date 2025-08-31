from __future__ import annotations

import abc
import datetime
from collections.abc import Iterable
from typing import Any

import jwt

from ...core import settings


class AbstractJWTHelper(abc.ABC):
    @abc.abstractmethod
    def encode(self,
               data: dict[str, Any],
               *,
               audience: str | Iterable[str] | None = None,
               lifetime: int | None = None) -> str: ...

    @abc.abstractmethod
    def decode(self,
               value: str,
               *,
               audience: str | Iterable[str] | None = None) -> dict[str, Any]: ...


class JWTHelper(AbstractJWTHelper):
    secret_key: str
    algorithm: str

    def __init__(self, *, secret_key: str | None = None, algorithm: str | None = None) -> None:
        self.secret_key = secret_key or settings.auth.secret_key
        self.algorithm = algorithm or 'HS256'

    def encode(self,
               data: dict[str, Any],
               *,
               audience: str | Iterable[str] | None = None,
               lifetime: int | None = None) -> str:
        payload = {
            **data,
        }

        if isinstance(audience, str):
            audience = [audience]

        if audience is not None:
            payload['aud'] = list(audience)

        if lifetime is not None:
            payload['exp'] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=lifetime)

        return jwt.encode(payload, key=self.secret_key, algorithm=self.algorithm)

    def decode(self,
               value: str,
               *,
               audience: str | Iterable[str] | None = None) -> dict[str, Any]:
        return jwt.decode(
            value,
            key=self.secret_key,
            audience=audience,
            algorithms=[self.algorithm],
        )

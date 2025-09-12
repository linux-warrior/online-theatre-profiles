from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import jwt

from .base import BaseTokenStrategy
from .....jwt import (
    AbstractJWTHelper,
    AbstractJWTService,
)


class JWTStrategy(BaseTokenStrategy):
    lifetime: int | None
    audience: Iterable[str]
    jwt_helper: AbstractJWTHelper

    def __init__(self,
                 *,
                 lifetime: int | None = None,
                 audience: str | Iterable[str] | None = None,
                 jwt_service: AbstractJWTService,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.lifetime = lifetime

        if audience is None:
            audience = 'users:auth'

        if isinstance(audience, str):
            audience = [audience]

        self.audience = audience
        self.jwt_helper = jwt_service.get_jwt_helper()

    def _decode_token(self, *, token: str) -> dict[str, Any] | None:
        try:
            return self.jwt_helper.decode(token, audience=self.audience)
        except jwt.PyJWTError:
            return None

    def _encode_token(self, *, data: dict[str, Any]) -> str:
        return self.jwt_helper.encode(
            data,
            audience=self.audience,
            lifetime=self.lifetime,
        )

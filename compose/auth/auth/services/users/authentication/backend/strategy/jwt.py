from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import jwt
import pydantic

from .base import (
    BaseTokenStrategy,
    TokenData,
)
from .exceptions import (
    InvalidToken,
)
from .....jwt import (
    AbstractJWTHelper,
    AbstractJWTService,
    JWTPayload,
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

    def decode_token(self, token: str) -> TokenData:
        try:
            jwt_payload = self.jwt_helper.decode(token, audience=self.audience)
        except jwt.PyJWTError:
            raise InvalidToken

        try:
            token_data = TokenData.model_validate({
                'token_id': jwt_payload.get('jti'),
                'user_id': jwt_payload.get('sub'),
                'parent_id': jwt_payload.get('parent_id'),
            })

        except pydantic.ValidationError:
            raise InvalidToken

        return token_data

    def encode_token(self, token_data: TokenData) -> str:
        token_dict = token_data.model_dump(mode='json')
        jwt_payload: JWTPayload = {
            'jti': token_dict['token_id'],
            'sub': token_dict['user_id'],
        }

        if token_dict['parent_id'] is not None:
            jwt_payload['parent_id'] = token_dict['parent_id']

        return self.jwt_helper.encode(
            jwt_payload,
            audience=self.audience,
            lifetime=self.lifetime,
        )

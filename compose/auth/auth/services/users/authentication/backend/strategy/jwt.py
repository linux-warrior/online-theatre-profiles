from __future__ import annotations

import abc
import dataclasses
import uuid
from collections.abc import Iterable
from typing import Any

import jwt

from .base import (
    AbstractTokenStrategy,
    Token,
)
from .exceptions import InvalidToken
from .processors import AbstractTokenProcessor
from .... import exceptions
from ....manager import UserManager
from .....jwt import (
    AbstractJWTHelper,
    AbstractJWTService,
)
from ......models.sqlalchemy import User


@dataclasses.dataclass(kw_only=True)
class TokenData:
    token_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    data: dict[str, Any]


class BaseTokenStrategy(AbstractTokenStrategy):
    token_processor: AbstractTokenProcessor

    def __init__(self,
                 *,
                 token_processor: AbstractTokenProcessor) -> None:
        self.token_processor = token_processor

    async def read_token(self, *, token: str, user_manager: UserManager) -> User | None:
        token_data = self.decode_token(token=token)

        if not token_data:
            return None

        user_id_str: str | None = token_data.data.get('sub')
        if user_id_str is None:
            return None

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            return None

        try:
            user = await user_manager.get(user_id)
        except exceptions.UserDoesNotExist:
            return None

        try:
            await self.token_processor.validate_token(token_id=token_data.token_id)
        except InvalidToken:
            return None

        return user

    def decode_token(self, *, token: str) -> TokenData | None:
        data = self._decode_token(token=token)

        if data is None:
            return None

        jti = data.get('jti')

        if jti is None:
            return None

        try:
            token_id = uuid.UUID(jti)
        except ValueError:
            return None

        parent_id: uuid.UUID | None = None
        parent_id_str = data.get('parent_id')

        if parent_id_str is not None:
            try:
                parent_id = uuid.UUID(parent_id_str)
            except ValueError:
                pass

        return TokenData(
            token_id=token_id,
            parent_id=parent_id,
            data=data,
        )

    @abc.abstractmethod
    def _decode_token(self, *, token: str) -> dict[str, Any] | None:
        ...

    async def write_token(self, *, user: User, parent_id: uuid.UUID | None = None) -> Token:
        token_id = uuid.uuid4()
        data = {
            'jti': str(token_id),
            'sub': str(user.id),
        }

        if parent_id is not None:
            data['parent_id'] = str(parent_id)

        token = self._encode_token(data=data)
        await self.token_processor.save_token(token_id=token_id)

        return Token(
            token_id=token_id,
            parent_id=parent_id,
            token=token,
        )

    @abc.abstractmethod
    def _encode_token(self, *, data: dict[str, Any]) -> str:
        ...

    async def destroy_token(self, *, token: str, user: User) -> Token | None:
        token_data = self.decode_token(token=token)

        if token_data is None:
            return None

        await self.token_processor.destroy_token(token_id=token_data.token_id)

        return Token(
            token_id=token_data.token_id,
            parent_id=token_data.parent_id,
            token=token,
        )

    async def destroy_token_id(self, *, token_id: uuid.UUID) -> None:
        await self.token_processor.destroy_token(token_id=token_id)


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

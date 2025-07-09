from __future__ import annotations

import dataclasses
import uuid
from collections.abc import Iterable
from typing import Any

import jwt

from .base import (
    AbstractTokenStrategy,
    Token,
)
from .... import exceptions
from ....manager import UserManager
from .....cache import (
    AbstractCache,
    AbstractCacheService,
)
from .....jwt import (
    AbstractJWTHelper,
    AbstractJWTService,
)
from ......models.sqlalchemy import User


class InvalidToken(Exception):
    pass


@dataclasses.dataclass(kw_only=True)
class TokenData:
    token_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    data: dict[str, Any]


class JWTStrategy(AbstractTokenStrategy):
    lifetime: int | None
    audience: Iterable[str]

    jwt_helper: AbstractJWTHelper
    cache: AbstractCache

    def __init__(self,
                 *,
                 lifetime: int | None = None,
                 audience: str | Iterable[str] | None = None,
                 jwt_service: AbstractJWTService,
                 cache_service: AbstractCacheService) -> None:
        self.lifetime = lifetime

        if audience is None:
            audience = 'users:auth'

        if isinstance(audience, str):
            audience = [audience]

        self.audience = audience

        self.jwt_helper = jwt_service.get_jwt_helper()
        self.cache = cache_service.get_cache(key_prefix='jwt')

    async def read_token(self, token: str, user_manager: UserManager) -> User | None:
        token_data = self._decode_token(token)

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
            await self._validate_token(token_data.token_id)
        except InvalidToken:
            return None

        return user

    def _decode_token(self, token: str) -> TokenData | None:
        try:
            data = self.jwt_helper.decode(token, audience=self.audience)
        except jwt.PyJWTError:
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

    async def _validate_token(self, token_id: uuid.UUID) -> None:
        pass

    async def write_token(self, user: User, parent_id: uuid.UUID | None = None) -> Token:
        token_id = uuid.uuid4()
        data = {
            'jti': str(token_id),
            'sub': str(user.id),
        }

        if parent_id is not None:
            data['parent_id'] = str(parent_id)

        token = self.jwt_helper.encode(
            data,
            audience=self.audience,
            lifetime=self.lifetime,
        )
        await self._save_token(token_id)

        return Token(
            token_id=token_id,
            parent_id=parent_id,
            token=token,
        )

    async def _save_token(self, token_id: uuid.UUID) -> None:
        pass

    async def destroy_token(self, token: str, user: User) -> Token | None:
        token_data = self._decode_token(token)

        if token_data is None:
            return None

        await self.destroy_token_id(token_data.token_id)

        return Token(
            token_id=token_data.token_id,
            parent_id=token_data.parent_id,
            token=token,
        )

    async def destroy_token_id(self, token_id: uuid.UUID) -> None:
        pass


class AccessJWTStrategy(JWTStrategy):
    async def _validate_token(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)

        if await self.cache.get(cache_key) is not None:
            raise InvalidToken

    async def destroy_token_id(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)
        await self.cache.set(cache_key, 'access', timeout=self.lifetime)

    def _create_cache_key(self, token_id: uuid.UUID) -> str:
        return f'access-{token_id}'


class RefreshJWTStrategy(JWTStrategy):
    async def _validate_token(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)

        if await self.cache.get(cache_key) is None:
            raise InvalidToken

    async def _save_token(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)
        await self.cache.set(cache_key, 'refresh', timeout=self.lifetime)

    async def destroy_token_id(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)
        await self.cache.delete(cache_key)

    def _create_cache_key(self, token_id: uuid.UUID) -> str:
        return f'refresh-{token_id}'

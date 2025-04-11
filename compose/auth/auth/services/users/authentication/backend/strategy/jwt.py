from __future__ import annotations

import dataclasses
import uuid

import jwt

from .base import (
    Strategy,
    Token,
)
from .... import exceptions
from ....jwt import (
    SecretType,
    decode_jwt,
    generate_jwt,
)
from ....manager import UserManager
from .....cache import (
    AbstractCache,
    AbstractCacheService,
)
from ......models.sqlalchemy import User


class InvalidToken(Exception):
    pass


@dataclasses.dataclass(kw_only=True)
class TokenData:
    token_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    data: dict


class JWTStrategy(Strategy):
    secret: SecretType
    lifetime_seconds: int | None
    token_audience: list[str]
    algorithm: str
    public_key: SecretType | None

    cache: AbstractCache

    def __init__(self,
                 *,
                 secret: SecretType,
                 lifetime_seconds: int | None = None,
                 token_audience: list[str] | None = None,
                 algorithm: str = 'HS256',
                 public_key: SecretType | None = None,
                 cache_service: AbstractCacheService) -> None:
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds

        if token_audience is None:
            token_audience = ['users:auth']

        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key

        self.cache = cache_service.get_cache(key_prefix='jwt')

    @property
    def encode_key(self) -> SecretType:
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        return self.public_key or self.secret

    async def read_token(self, token: str, user_manager: UserManager) -> User | None:
        token_data = self._decode_token(token)

        if not token_data:
            return None

        user_id = token_data.data.get('sub')
        if user_id is None:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
        except exceptions.InvalidID:
            return None

        try:
            user = await user_manager.get(parsed_id)
        except exceptions.UserDoesNotExist:
            return None

        try:
            await self._validate_token(token_data.token_id)
        except InvalidToken:
            return None

        return user

    def _decode_token(self, token: str) -> TokenData | None:
        try:
            data = decode_jwt(
                token,
                secret=self.decode_key,
                audience=self.token_audience,
                algorithms=[self.algorithm],
            )
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

        return TokenData(token_id=token_id, parent_id=parent_id, data=data)

    async def _validate_token(self, token_id: uuid.UUID) -> None:
        pass

    async def write_token(self, user: User, parent_id: uuid.UUID | None = None) -> Token:
        token_id = uuid.uuid4()
        data = {
            'jti': str(token_id),
            'sub': str(user.id),
            'aud': self.token_audience,
        }

        if parent_id is not None:
            data['parent_id'] = str(parent_id)

        token = generate_jwt(
            data,
            secret=self.encode_key,
            lifetime_seconds=self.lifetime_seconds,
            algorithm=self.algorithm,
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
        await self.cache.set(cache_key, 'access', timeout=self.lifetime_seconds)

    def _create_cache_key(self, token_id: uuid.UUID) -> str:
        return f'access-{token_id}'


class RefreshJWTStrategy(JWTStrategy):
    async def _validate_token(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)

        if await self.cache.get(cache_key) is None:
            raise InvalidToken

    async def _save_token(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)
        await self.cache.set(cache_key, 'refresh', timeout=self.lifetime_seconds)

    async def destroy_token_id(self, token_id: uuid.UUID) -> None:
        cache_key = self._create_cache_key(token_id)
        await self.cache.delete(cache_key)

    def _create_cache_key(self, token_id: uuid.UUID) -> str:
        return f'refresh-{token_id}'

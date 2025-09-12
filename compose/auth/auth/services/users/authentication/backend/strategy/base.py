from __future__ import annotations

import abc
import uuid

from .exceptions import InvalidToken
from .models import (
    Token,
    TokenData,
)
from .processors import AbstractTokenProcessor
from ....exceptions import UserDoesNotExist
from ....manager import UserManager
from ......models.sqlalchemy import User


class AbstractTokenStrategy(abc.ABC):
    @abc.abstractmethod
    async def read_token(self, *, token: str, user_manager: UserManager) -> User | None: ...

    @abc.abstractmethod
    async def write_token(self, *, user: User, parent_id: uuid.UUID | None = None) -> Token: ...

    @abc.abstractmethod
    async def destroy_token(self, *, token: str, user: User) -> Token | None: ...

    @abc.abstractmethod
    async def destroy_token_id(self, *, token_id: uuid.UUID) -> None: ...


class BaseTokenStrategy(AbstractTokenStrategy):
    token_processor: AbstractTokenProcessor

    def __init__(self,
                 *,
                 token_processor: AbstractTokenProcessor) -> None:
        self.token_processor = token_processor

    async def read_token(self, *, token: str, user_manager: UserManager) -> User | None:
        try:
            token_data = self.decode_token(token=token)
        except InvalidToken:
            return None

        try:
            await self.token_processor.validate_token(token_id=token_data.token_id)
        except InvalidToken:
            return None

        try:
            user = await user_manager.get(token_data.user_id)
        except UserDoesNotExist:
            return None

        return user

    @abc.abstractmethod
    def decode_token(self, token: str) -> TokenData:
        ...

    async def write_token(self, *, user: User, parent_id: uuid.UUID | None = None) -> Token:
        token_data = TokenData(
            token_id=uuid.uuid4(),
            user_id=user.id,
            parent_id=parent_id,
        )
        token = self.encode_token(token_data)

        await self.token_processor.save_token(token_id=token_data.token_id)

        return Token(
            token_id=token_data.token_id,
            parent_id=parent_id,
            token=token,
        )

    @abc.abstractmethod
    def encode_token(self, token_data: TokenData) -> str:
        ...

    async def destroy_token(self, *, token: str, user: User) -> Token | None:
        try:
            token_data = self.decode_token(token=token)
        except InvalidToken:
            return None

        await self.token_processor.destroy_token(token_id=token_data.token_id)

        return Token(
            token_id=token_data.token_id,
            parent_id=token_data.parent_id,
            token=token,
        )

    async def destroy_token_id(self, *, token_id: uuid.UUID) -> None:
        await self.token_processor.destroy_token(token_id=token_id)

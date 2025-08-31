from __future__ import annotations

from fastapi import Response, status

from .strategy import (
    AbstractTokenStrategy,
)
from .transport import (
    AbstractTokenTransport,
    LogoutNotSupportedError,
)
from ...manager import UserManager
from .....models.sqlalchemy import User


class AuthenticationBackend:
    name: str
    transport: AbstractTokenTransport
    access_token_strategy: AbstractTokenStrategy
    refresh_token_strategy: AbstractTokenStrategy

    def __init__(
            self,
            name: str,
            transport: AbstractTokenTransport,
            access_token_strategy: AbstractTokenStrategy,
            refresh_token_strategy: AbstractTokenStrategy,
    ) -> None:
        self.name = name
        self.transport = transport
        self.access_token_strategy = access_token_strategy
        self.refresh_token_strategy = refresh_token_strategy

    async def authenticate(self, token: str, user_manager: UserManager) -> User | None:
        return await self.access_token_strategy.read_token(
            token=token,
            user_manager=user_manager,
        )

    async def authenticate_refresh(self, token: str, user_manager: UserManager) -> User | None:
        return await self.refresh_token_strategy.read_token(
            token=token,
            user_manager=user_manager,
        )

    async def login(self, user: User) -> Response:
        refresh_token = await self.refresh_token_strategy.write_token(user=user)
        access_token = await self.access_token_strategy.write_token(
            user=user,
            parent_id=refresh_token.token_id,
        )

        return await self.transport.get_login_response(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
        )

    async def logout(self, user: User, token: str) -> Response:
        access_token = await self.access_token_strategy.destroy_token(token=token, user=user)

        if access_token is not None and access_token.parent_id:
            await self.refresh_token_strategy.destroy_token_id(token_id=access_token.parent_id)

        try:
            response = await self.transport.get_logout_response()
        except LogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response

    async def refresh(self, user: User, token: str) -> Response:
        await self.refresh_token_strategy.destroy_token(token=token, user=user)

        refresh_token = await self.refresh_token_strategy.write_token(user=user)
        access_token = await self.access_token_strategy.write_token(
            user=user,
            parent_id=refresh_token.token_id,
        )

        return await self.transport.get_refresh_response(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
        )

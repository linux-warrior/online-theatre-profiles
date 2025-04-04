from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Response, status

from .strategy import (
    Strategy,
    AccessStrategyDep,
    RefreshStrategyDep,
)
from .transport import (
    Transport,
    TransportDep,
    TransportLogoutNotSupportedError,
)
from ...manager import UserManager
from .....models.sqlalchemy import User


class AuthenticationBackend:
    name: str
    transport: Transport
    access_strategy: Strategy
    refresh_strategy: Strategy

    def __init__(
            self,
            name: str,
            transport: Transport,
            access_strategy: Strategy,
            refresh_strategy: Strategy,
    ):
        self.name = name
        self.transport = transport
        self.access_strategy = access_strategy
        self.refresh_strategy = refresh_strategy

    async def authenticate(self, token: str, user_manager: UserManager) -> User | None:
        return await self.access_strategy.read_token(
            token=token,
            user_manager=user_manager,
        )

    async def authenticate_refresh(self, token: str, user_manager: UserManager) -> User | None:
        return await self.refresh_strategy.read_token(
            token=token,
            user_manager=user_manager,
        )

    async def login(self, user: User) -> Response:
        refresh_token = await self.refresh_strategy.write_token(user)
        access_token = await self.access_strategy.write_token(user, parent_id=refresh_token.token_id)

        return await self.transport.get_login_response(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
        )

    async def logout(self, user: User, token: str) -> Response:
        access_token = await self.access_strategy.destroy_token(token=token, user=user)

        if access_token is not None and access_token.parent_id:
            await self.refresh_strategy.destroy_token_id(access_token.parent_id)

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response

    async def refresh(self, user: User, token: str) -> Response:
        await self.refresh_strategy.destroy_token(token=token, user=user)

        refresh_token = await self.refresh_strategy.write_token(user)
        access_token = await self.access_strategy.write_token(user, parent_id=refresh_token.token_id)

        return await self.transport.get_refresh_response(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
        )


async def get_authentication_backend(transport: TransportDep,
                                     access_strategy: AccessStrategyDep,
                                     refresh_strategy: RefreshStrategyDep) -> AuthenticationBackend:
    return AuthenticationBackend(
        name='jwt',
        transport=transport,
        access_strategy=access_strategy,
        refresh_strategy=refresh_strategy,
    )


AuthenticationBackendDep = Annotated[AuthenticationBackend, Depends(get_authentication_backend)]

from __future__ import annotations

import abc
import uuid
from collections.abc import Iterable
from typing import Annotated

from fastapi import (
    Request,
    Response,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm

from .authentication import (
    AuthenticationBackend,
    AuthenticationBackendDep,
)
from .exceptions import (
    InvalidToken,
    OAuthInvalidProvider,
    OAuthInvalidStateToken,
    OAuthEmailNotAvailable,
)
from .manager import (
    UserManager,
    UserManagerDep,
)
from .models import (
    ReadUserResponse,
    UserCreate,
    UserUpdate,
    OAuth2AuthorizeResponse,
)
from .oauth import (
    AbstractOAuthService,
    OAuthServiceDep,
    InvalidOAuthProvider,
    InvalidStateToken,
)
from ..extended_users import (
    AbstractExtendedUserService,
    ExtendedUserServiceDep,
    ExtendedCurrentUserResponse,
    ExtendedReadUserResponse,
)
from ..pagination import (
    PageParams,
)
from ...models.sqlalchemy import User


class AbstractUserService(abc.ABC):
    @abc.abstractmethod
    async def login(self, *, request: Request, credentials: OAuth2PasswordRequestForm) -> Response: ...

    @abc.abstractmethod
    async def logout(self, *, user: User, token: str) -> Response: ...

    @abc.abstractmethod
    async def refresh(self, *, refresh_token: str) -> Response: ...

    @abc.abstractmethod
    async def register(self, *, user_create: UserCreate) -> ExtendedCurrentUserResponse: ...

    @abc.abstractmethod
    async def get_current_user(self, *, user: User) -> ExtendedCurrentUserResponse: ...

    @abc.abstractmethod
    async def patch_current_user(self, *, user: User, user_update: UserUpdate) -> ExtendedCurrentUserResponse: ...

    @abc.abstractmethod
    async def get_user(self, *, user_id: uuid.UUID) -> ExtendedReadUserResponse: ...

    @abc.abstractmethod
    async def get_users_list(self, *, page_params: PageParams) -> list[ReadUserResponse]: ...

    @abc.abstractmethod
    async def oauth_authorize(self,
                              *,
                              request: Request,
                              provider_name: str,
                              scope: Iterable[str] | None = None) -> OAuth2AuthorizeResponse: ...

    @abc.abstractmethod
    async def oauth_callback(self,
                             *,
                             request: Request,
                             provider_name: str,
                             code: str | None = None,
                             code_verifier: str | None = None,
                             state: str | None = None,
                             error: str | None = None) -> Response: ...


class UserService(AbstractUserService):
    auth_backend: AuthenticationBackend
    user_manager: UserManager
    oauth_service: AbstractOAuthService
    ext_user_service: AbstractExtendedUserService

    def __init__(self,
                 *,
                 user_manager: UserManager,
                 oauth_service: AbstractOAuthService,
                 auth_backend: AuthenticationBackend,
                 ext_user_service: AbstractExtendedUserService) -> None:
        self.user_manager = user_manager
        self.oauth_service = oauth_service
        self.auth_backend = auth_backend
        self.ext_user_service = ext_user_service

    async def login(self, *, request: Request, credentials: OAuth2PasswordRequestForm) -> Response:
        user = await self.user_manager.authenticate(
            request=request,
            credentials=credentials,
        )
        return await self.auth_backend.login(user)

    async def logout(self, *, user: User, token: str) -> Response:
        return await self.auth_backend.logout(user=user, token=token)

    async def refresh(self, *, refresh_token: str) -> Response:
        user = await self.auth_backend.authenticate_refresh(
            user_manager=self.user_manager,
            token=refresh_token,
        )

        if user is None:
            raise InvalidToken(message='REFRESH_INVALID_TOKEN')

        return await self.auth_backend.refresh(user=user, token=refresh_token)

    async def register(self, *, user_create: UserCreate) -> ExtendedCurrentUserResponse:
        user = await self.user_manager.create(user_create=user_create)
        return await self.ext_user_service.extend_current_user(user=user)

    async def get_current_user(self, *, user: User) -> ExtendedCurrentUserResponse:
        return await self.ext_user_service.extend_current_user(user=user)

    async def patch_current_user(self, *, user: User, user_update: UserUpdate) -> ExtendedCurrentUserResponse:
        user = await self.user_manager.update(user=user, user_update=user_update)
        return await self.ext_user_service.extend_current_user(user=user)

    async def get_user(self, *, user_id: uuid.UUID) -> ExtendedReadUserResponse:
        user = await self.user_manager.get(user_id=user_id)
        return await self.ext_user_service.extend_user(user=user)

    async def get_users_list(self, *, page_params: PageParams) -> list[ReadUserResponse]:
        users_list = await self.user_manager.get_list(page_params=page_params)

        return [
            ReadUserResponse.model_validate(user, from_attributes=True)
            for user in users_list
        ]

    async def oauth_authorize(self,
                              *,
                              request: Request,
                              provider_name: str,
                              scope: Iterable[str] | None = None) -> OAuth2AuthorizeResponse:
        try:
            authorization_url = await self.oauth_service.get_authorization_url(
                request=request,
                provider_name=provider_name,
                scope=scope,
            )

        except InvalidOAuthProvider:
            raise OAuthInvalidProvider

        return OAuth2AuthorizeResponse(authorization_url=authorization_url)

    async def oauth_callback(self,
                             *,
                             request: Request,
                             provider_name: str,
                             code: str | None = None,
                             code_verifier: str | None = None,
                             state: str | None = None,
                             error: str | None = None) -> Response:
        try:
            oauth_result = await self.oauth_service.authorize(
                request=request,
                provider_name=provider_name,
                code=code,
                code_verifier=code_verifier,
                state=state,
                error=error,
            )

        except InvalidOAuthProvider:
            raise OAuthInvalidProvider

        except InvalidStateToken:
            raise OAuthInvalidStateToken

        if oauth_result.user_email is None:
            raise OAuthEmailNotAvailable

        user = await self.user_manager.oauth_callback(
            oauth_name=oauth_result.client_name,
            access_token=oauth_result.token['access_token'],
            account_id=oauth_result.user_id,
            account_email=oauth_result.user_email,
            expires_at=oauth_result.token.get('expires_at'),
            refresh_token=oauth_result.token.get('refresh_token'),
        )

        return await self.auth_backend.login(user)


async def get_user_service(user_manager: UserManagerDep,
                           auth_backend: AuthenticationBackendDep,
                           oauth_service: OAuthServiceDep,
                           ext_user_service: ExtendedUserServiceDep) -> AbstractUserService:
    return UserService(
        user_manager=user_manager,
        auth_backend=auth_backend,
        oauth_service=oauth_service,
        ext_user_service=ext_user_service,
    )


UserServiceDep = Annotated[AbstractUserService, Depends(get_user_service)]

from __future__ import annotations

import abc
import dataclasses
from typing import ClassVar, Annotated

import jwt
from fastapi import Request, Depends
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token

from .client import (
    AbstractOAuthClientService,
    OAuthClientServiceDep,
)
from .exceptions import (
    InvalidOAuthProvider,
    InvalidStateToken,
)
from ..jwt import (
    generate_jwt,
    decode_jwt,
)
from ....core import settings


@dataclasses.dataclass(kw_only=True)
class OAuthAuthorizeResult:
    client_name: str
    token: OAuth2Token
    user_id: str
    user_email: str | None = None


class AbstractOAuthService(abc.ABC):
    @abc.abstractmethod
    async def get_authorization_url(self,
                                    *,
                                    request: Request,
                                    provider_name: str,
                                    scope: list[str] | None = None) -> str: ...

    @abc.abstractmethod
    async def authorize(self,
                        *,
                        request: Request,
                        provider_name: str,
                        code: str | None = None,
                        code_verifier: str | None = None,
                        state: str | None = None,
                        error: str | None = None) -> OAuthAuthorizeResult: ...


class OAuthService(AbstractOAuthService):
    state_token_audience: ClassVar[str] = 'users:oauth-state:{provider_name}'

    oauth_client_service: AbstractOAuthClientService

    def __init__(self, *, oauth_client_service: AbstractOAuthClientService) -> None:
        self.oauth_client_service = oauth_client_service

    async def get_authorization_url(self,
                                    *,
                                    request: Request,
                                    provider_name: str,
                                    scope: list[str] | None = None) -> str:
        oauth_client = self._create_oauth_client(provider_name=provider_name)

        authorize_redirect_url = str(request.url_for('oauth:callback', provider_name=provider_name))
        audience = self._get_state_token_audience(provider_name=provider_name)
        state = generate_jwt({
            'aud': audience,
        }, secret=settings.auth.secret_key)

        return await oauth_client.get_authorization_url(
            authorize_redirect_url,
            state=state,
            scope=scope,
        )

    async def authorize(self,
                        *,
                        request: Request,
                        provider_name: str,
                        code: str | None = None,
                        code_verifier: str | None = None,
                        state: str | None = None,
                        error: str | None = None) -> OAuthAuthorizeResult:
        oauth_client = self._create_oauth_client(provider_name=provider_name)

        if not state:
            raise InvalidStateToken(state='')

        audience = self._get_state_token_audience(provider_name=provider_name)
        try:
            decode_jwt(state, secret=settings.auth.secret_key, audience=[audience])
        except jwt.DecodeError:
            raise InvalidStateToken(state=state)

        authorize_callback_url = str(request.url_for('oauth:callback', provider_name=provider_name))
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            redirect_url=authorize_callback_url,
        )
        token, state = await oauth2_authorize_callback(
            request,
            code=code,
            code_verifier=code_verifier,
            state=state,
            error=error,
        )

        user_id, user_email = await oauth_client.get_id_email(token['access_token'])

        return OAuthAuthorizeResult(
            client_name=oauth_client.name,
            token=token,
            user_id=user_id,
            user_email=user_email,
        )

    def _create_oauth_client(self, *, provider_name: str) -> BaseOAuth2:
        oauth_client = self.oauth_client_service.create_client(provider_name=provider_name)
        if oauth_client is None:
            raise InvalidOAuthProvider(provider_name=provider_name)

        return oauth_client

    def _get_state_token_audience(self, *, provider_name: str) -> str:
        return self.state_token_audience.format(provider_name=provider_name)


async def get_oauth_service(oauth_client_service: OAuthClientServiceDep) -> AbstractOAuthService:
    return OAuthService(oauth_client_service=oauth_client_service)


OAuthServiceDep = Annotated[AbstractOAuthService, Depends(get_oauth_service)]

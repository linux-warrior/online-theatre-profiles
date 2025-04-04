from __future__ import annotations

import time
from typing import Any, Type

import httpx
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import (
    BaseOAuth2,
    OAuth2Token,
    RefreshTokenNotSupportedError,
    OAuth2RequestError,
)

from .base import BaseOAuthClientFactory
from ......core import settings


class GoogleOAuthClientFactory(BaseOAuthClientFactory):
    def get_client_class(self) -> Type[BaseOAuth2]:
        return GoogleOAuth2

    def get_client_kwargs(self) -> dict:
        return {
            'client_id': settings.oauth.google_client_id,
            'client_secret': settings.oauth.google_client_secret,
        }


class FakeGoogleOAuth2(GoogleOAuth2):
    async def get_access_token(self,
                               code: str,
                               redirect_uri: str,
                               code_verifier: str | None = None) -> OAuth2Token:
        return OAuth2Token({
            'access_token': 'access_token',
            'expires_in': 3600,
            'scope': (
                'openid '
                'https://www.googleapis.com/auth/userinfo.profile '
                'https://www.googleapis.com/auth/userinfo.email'
            ),
            'token_type': 'Bearer',
            'id_token': 'id_token',
            'expires_at': int(time.time()),
        })

    async def refresh_token(self, refresh_token: str) -> OAuth2Token:
        raise RefreshTokenNotSupportedError

    async def revoke_token(self, token: str, token_type_hint: str | None = None) -> None:
        return None

    async def get_profile(self, token: str) -> dict[str, Any]:
        return {
            'resourceName': 'people/1',
            'etag': 'test',
            'emailAddresses': [
                {
                    'metadata': {
                        'primary': True,
                        'verified': True,
                        'source': {
                            'type': 'ACCOUNT',
                            'id': '1',
                        },
                        'sourcePrimary': True,
                    },
                    'value': 'user@gmail.com',
                },
            ],
        }

    async def send_request(
            self,
            client: httpx.AsyncClient,
            request: httpx.Request,
            auth: httpx.Auth | None,
            *,
            exc_class: type[OAuth2RequestError],
    ) -> httpx.Response:
        return httpx.Response(status_code=200, json={})


class FakeGoogleOAuthClientFactory(BaseOAuthClientFactory):
    def get_client_class(self) -> Type[BaseOAuth2]:
        return FakeGoogleOAuth2

    def get_client_kwargs(self) -> dict:
        return {
            'client_id': 'client_id',
            'client_secret': 'client_secret',
        }

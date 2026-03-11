from __future__ import annotations

import httpx

from .config import auth_config
from .schemas import AuthTokens
from ..http import HttpClient


class AuthTokensProcessor:
    _http_client: HttpClient
    _user_login: str
    _user_password: str

    _auth_tokens: AuthTokens | None

    def __init__(self,
                 *,
                 httpx_client: httpx.Client,
                 user_login: str,
                 user_password: str) -> None:
        self._http_client = HttpClient(
            httpx_client=httpx_client,
            base_url=auth_config.api_v1_url,
        )
        self._user_login = user_login
        self._user_password = user_password

        self._auth_tokens = None

    def login(self) -> AuthTokens:
        if self._auth_tokens is not None:
            return self._auth_tokens

        response = self._http_client.post(
            auth_config.get_login_url(),
            data={
                'grant_type': 'password',
                'username': self._user_login,
                'password': self._user_password,
            },
        )

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens

    def refresh(self) -> AuthTokens:
        if self._auth_tokens is None:
            return self.login()

        response = self._http_client.post(
            auth_config.get_refresh_url(),
            data={
                'refresh_token': self._auth_tokens.refresh_token,
            },
        )

        self._auth_tokens = AuthTokens.model_validate(response.json())
        return self._auth_tokens

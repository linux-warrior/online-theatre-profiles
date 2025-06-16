from __future__ import annotations

import httpx

from .client import AuthServiceClient
from .schemas import (
    CurrentUser,
)
from .tokens import AuthTokensProcessor


class AuthService:
    auth_service_client: AuthServiceClient

    def __init__(self,
                 *,
                 user_login: str,
                 user_password: str) -> None:
        httpx_client = httpx.Client()
        auth_tokens_processor = AuthTokensProcessor(
            httpx_client=httpx_client,
            user_login=user_login,
            user_password=user_password,
        )
        self.auth_service_client = AuthServiceClient(
            httpx_client=httpx_client,
            auth_tokens_processor=auth_tokens_processor,
        )

    def get_user_profile(self) -> CurrentUser:
        return self.auth_service_client.get_user_profile()

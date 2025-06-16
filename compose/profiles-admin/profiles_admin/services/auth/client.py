from __future__ import annotations

from typing import Any

import httpx

from .config import auth_config
from .schemas import (
    AuthTokens,
    CurrentUser,
)
from .tokens import (
    AuthTokensProcessor,
)
from ..http import (
    HttpClient,
    HttpResponse,
)


class AuthServiceClient:
    http_client: HttpClient

    def __init__(self,
                 *,
                 httpx_client: httpx.Client,
                 auth_tokens_processor: AuthTokensProcessor) -> None:
        self.http_client = AuthenticatedHttpClient(
            httpx_client=httpx_client,
            base_url=auth_config.api_v1_url,
            auth_tokens_processor=auth_tokens_processor,
        )

    def get_user_profile(self) -> CurrentUser:
        response = self.http_client.get(
            url=auth_config.get_user_profile_url(),
        )

        return CurrentUser.model_validate(response.json())


class AuthenticatedHttpClient(HttpClient):
    auth_tokens_processor: AuthTokensProcessor

    def __init__(self, *, auth_tokens_processor: AuthTokensProcessor, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.auth_tokens_processor = auth_tokens_processor

    def send_request(self,
                     method: str,
                     url: str,
                     *,
                     headers: dict | None = None,
                     **kwargs: Any) -> HttpResponse:
        auth_tokens = self.auth_tokens_processor.login()

        try:
            return self._send_authenticated_request(
                method,
                url,
                headers=headers,
                auth_tokens=auth_tokens,
                **kwargs,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == httpx.codes.UNAUTHORIZED:
                auth_tokens = self.auth_tokens_processor.refresh()

                return self._send_authenticated_request(
                    method,
                    url,
                    headers=headers,
                    auth_tokens=auth_tokens,
                    **kwargs,
                )

            else:
                raise

    def _send_authenticated_request(self,
                                    method: str,
                                    url: str,
                                    *,
                                    headers: dict | None = None,
                                    auth_tokens: AuthTokens,
                                    **kwargs: Any) -> HttpResponse:
        token_headers: dict = {
            'Authorization': f'Bearer {auth_tokens.access_token}',
        }

        return super().send_request(
            method,
            url,
            headers={
                **token_headers,
                **(headers or {}),
            },
            **kwargs,
        )

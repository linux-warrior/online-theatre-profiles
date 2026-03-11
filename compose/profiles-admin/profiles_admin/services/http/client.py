from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import httpx


class HttpClient:
    _httpx_client: httpx.Client
    _base_url: str | None
    _headers: dict

    def __init__(self,
                 *,
                 httpx_client: httpx.Client,
                 base_url: str | None = None,
                 headers: dict | None = None) -> None:
        self._httpx_client = httpx_client
        self._base_url = base_url
        self._headers = headers or {}

    def get(self,
            url: str,
            *,
            params: dict | None = None,
            headers: dict | None = None) -> HttpResponse:
        return self.send_request(
            'GET',
            url,
            params=params,
            headers=headers,
        )

    def post(self,
             url: str,
             *,
             data: dict | None = None,
             json: dict | None = None,
             params: dict | None = None,
             headers: dict | None = None) -> HttpResponse:
        return self.send_request(
            'POST',
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
        )

    def send_request(self,
                     method: str,
                     url: str,
                     *,
                     data: dict | None = None,
                     json: dict | None = None,
                     params: dict | None = None,
                     headers: dict | None = None) -> HttpResponse:
        request_url = self.get_request_url(url)
        request_headers = self.get_request_headers(headers)

        response = self._httpx_client.request(
            method,
            request_url,
            data=data,
            json=json,
            params=params,
            headers=request_headers,
        )
        response.raise_for_status()

        return HttpResponse(response=response)

    def get_request_url(self, url: str) -> str:
        if not self._base_url:
            return url

        return urljoin(self._base_url, url)

    def get_request_headers(self, headers: dict | None = None) -> dict:
        return {
            **self.get_default_headers(),
            **self._headers,
            **(headers or {}),
        }

    def get_default_headers(self) -> dict:
        return {
            'X-Request-Id': 'profiles-admin',
        }


class HttpResponse:
    _response: httpx.Response

    def __init__(self, *, response: httpx.Response) -> None:
        self._response = response

    def json(self) -> Any:
        return self._response.json()

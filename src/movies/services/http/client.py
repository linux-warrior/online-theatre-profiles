from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import httpx


class HttpClient:
    httpx_client: httpx.AsyncClient
    base_url: str | None
    headers: dict

    def __init__(self,
                 *,
                 httpx_client: httpx.AsyncClient,
                 base_url: str | None = None,
                 headers: dict | None = None) -> None:
        self.httpx_client = httpx_client
        self.base_url = base_url
        self.headers = headers or {}

    async def get(self,
                  url: str,
                  *,
                  params: dict | None = None,
                  headers: dict | None = None) -> HttpResponse:
        return await self.send_request(
            'GET',
            url,
            params=params,
            headers=headers,
        )

    async def post(self,
                   url: str,
                   *,
                   data: dict | None = None,
                   json: dict | None = None,
                   params: dict | None = None,
                   headers: dict | None = None) -> HttpResponse:
        return await self.send_request(
            'POST',
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
        )

    async def send_request(self,
                           method: str,
                           url: str,
                           *,
                           data: dict | None = None,
                           json: dict | None = None,
                           params: dict | None = None,
                           headers: dict | None = None) -> HttpResponse:
        request_url = self.get_request_url(url)
        request_headers = self.get_request_headers(headers)

        response = await self.httpx_client.request(
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
        if not self.base_url:
            return url

        return urljoin(self.base_url, url)

    def get_request_headers(self, headers: dict | None = None) -> dict:
        return {
            **self.get_default_headers(),
            **self.headers,
            **(headers or {}),
        }

    def get_default_headers(self) -> dict:
        return {
            'X-Request-Id': 'movies',
        }


class HttpResponse:
    response: httpx.Response

    def __init__(self, *, response: httpx.Response) -> None:
        self.response = response

    def json(self) -> Any:
        return self.response.json()

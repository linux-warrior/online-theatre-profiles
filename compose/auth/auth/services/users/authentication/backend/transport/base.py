from __future__ import annotations

from typing import Protocol

from fastapi import Response


class TransportLogoutNotSupportedError(Exception):
    pass


class Transport(Protocol):
    async def get_login_response(self, access_token: str, refresh_token: str) -> Response: ...

    async def get_logout_response(self) -> Response: ...

    async def get_refresh_response(self, access_token: str, refresh_token: str) -> Response: ...

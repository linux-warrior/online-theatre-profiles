from __future__ import annotations

import abc

from fastapi import Response


class LogoutNotSupportedError(Exception):
    pass


class AbstractTokenTransport(abc.ABC):
    @abc.abstractmethod
    async def get_login_response(self, *, access_token: str, refresh_token: str) -> Response: ...

    @abc.abstractmethod
    async def get_logout_response(self) -> Response: ...

    @abc.abstractmethod
    async def get_refresh_response(self, *, access_token: str, refresh_token: str) -> Response: ...

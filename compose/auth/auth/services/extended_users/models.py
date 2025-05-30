from __future__ import annotations

from ...services.users import (
    CurrentUserResponse,
    ReadUserResponse,
)


class ExtendedCurrentUserResponse(CurrentUserResponse):
    permissions: list[str] = []


class ExtendedReadUserResponse(ReadUserResponse):
    permissions: list[str] = []

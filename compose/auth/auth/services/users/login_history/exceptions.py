from __future__ import annotations

from ...common import BaseServiceException


class LoginHistoryServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Login history service exception'


class LoginHistoryCreateError(LoginHistoryServiceException):
    def get_default_message(self) -> str:
        return 'Login history create error'

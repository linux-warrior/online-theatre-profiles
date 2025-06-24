from __future__ import annotations

from ...common import BaseServiceException


class UserRoleServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'User role service exception'


class UserRoleNotFound(UserRoleServiceException):
    def get_default_message(self) -> str:
        return 'User role not found'


class UserRoleCreateError(UserRoleServiceException):
    def get_default_message(self) -> str:
        return 'User role create error'

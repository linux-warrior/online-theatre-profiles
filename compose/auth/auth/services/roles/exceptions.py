from __future__ import annotations

from ..base import BaseServiceException


class RoleServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Role service exception'


class RoleNotFound(RoleServiceException):
    def get_default_message(self) -> str:
        return 'Role not found'


class RoleAlreadyExists(RoleServiceException):
    def get_default_message(self) -> str:
        return 'Role already exists'

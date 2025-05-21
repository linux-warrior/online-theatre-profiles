from __future__ import annotations

from ..base import (
    BaseServiceException,
)


class PermissionServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Permission service exception'


class PermissionNotFound(PermissionServiceException):
    def get_default_message(self) -> str:
        return 'Permission not found'


class PermissionAlreadyExists(PermissionServiceException):
    def get_default_message(self) -> str:
        return 'Permission already exists'

from __future__ import annotations

from ...base import BaseServiceException


class RolePermissionServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Role permission service exception'


class RolePermissionNotFound(RolePermissionServiceException):
    def get_default_message(self) -> str:
        return 'Role permission not found'


class RolePermissionCreateError(RolePermissionServiceException):
    def get_default_message(self) -> str:
        return 'Role permission create error'

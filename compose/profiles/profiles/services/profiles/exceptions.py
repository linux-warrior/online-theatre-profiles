from __future__ import annotations

from ..common import (
    BaseServiceException,
)


class ProfileServiceException(BaseServiceException):
    def get_default_message(self) -> str:
        return 'Profile service exception'


class ProfileNotFound(ProfileServiceException):
    def get_default_message(self) -> str:
        return 'Profile not found'


class ProfileCreateError(ProfileServiceException):
    def get_default_message(self) -> str:
        return 'Profile create error'


class ProfileUpdateError(ProfileServiceException):
    def get_default_message(self) -> str:
        return 'Profile update error'

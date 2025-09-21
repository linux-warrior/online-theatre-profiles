from __future__ import annotations

import abc

from ..common import (
    BaseServiceException,
)


class UserServiceException(BaseServiceException, abc.ABC):
    pass


class UserDoesNotExist(UserServiceException):
    def get_default_message(self) -> str:
        return 'USER_DOES_NOT_EXIST'


class UserAlreadyExists(UserServiceException):
    def get_default_message(self) -> str:
        return 'USER_ALREADY_EXISTS'


class BadCredentials(UserServiceException):
    def get_default_message(self) -> str:
        return 'BAD_CREDENTIALS'


class InvalidToken(UserServiceException):
    def get_default_message(self) -> str:
        return 'INVALID_TOKEN'


class OAuthInvalidProvider(UserServiceException):
    def get_default_message(self) -> str:
        return 'OAUTH_INVALID_PROVIDER'


class OAuthInvalidStateToken(UserServiceException):
    def get_default_message(self) -> str:
        return 'OAUTH_INVALID_STATE_TOKEN'


class OAuthEmailNotAvailable(UserServiceException):
    def get_default_message(self) -> str:
        return 'OAUTH_EMAIL_NOT_AVAILABLE'

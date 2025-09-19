from __future__ import annotations

import abc

from ..common import (
    BaseServiceException,
)


class UserException(BaseServiceException, abc.ABC):
    pass


class UserDoesNotExist(UserException):
    def get_default_message(self) -> str:
        return 'USER_DOES_NOT_EXIST'


class UserAlreadyExists(UserException):
    def get_default_message(self) -> str:
        return 'USER_ALREADY_EXISTS'


class BadCredentials(UserException):
    def get_default_message(self) -> str:
        return 'BAD_CREDENTIALS'


class InvalidToken(UserException):
    def get_default_message(self) -> str:
        return 'INVALID_TOKEN'

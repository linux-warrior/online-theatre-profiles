from __future__ import annotations


class UsersException(Exception):
    pass


class UserDoesNotExist(UsersException):
    pass


class UserAlreadyExists(UsersException):
    pass

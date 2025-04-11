from __future__ import annotations


class UsersException(Exception):
    pass


class InvalidID(UsersException):
    pass


class UserDoesNotExist(UsersException):
    pass


class UserAlreadyExists(UsersException):
    pass

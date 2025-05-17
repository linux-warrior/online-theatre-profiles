from __future__ import annotations


class RoleServiceException(Exception):
    message: str | None
    description: str | None

    def __init__(self,
                 *,
                 message: str | None = None,
                 description: str | None = None) -> None:
        self.message = message
        self.description = description

    def __str__(self) -> str:
        message = self.get_message()
        description = self.get_description()

        if not description:
            return message

        return f'{message}: {description}'

    def get_message(self) -> str:
        return self.message or self.get_default_message()

    def get_default_message(self) -> str:
        return 'Role service exception'

    def get_description(self) -> str:
        return self.description or self.get_default_description()

    def get_default_description(self) -> str:
        return ''


class RoleNotFound(RoleServiceException):
    def get_default_message(self) -> str:
        return 'Role not found'


class RoleAlreadyExists(RoleServiceException):
    def get_default_message(self) -> str:
        return 'Role already exists'

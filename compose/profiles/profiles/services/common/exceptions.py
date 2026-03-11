from __future__ import annotations

import abc


class BaseServiceException(Exception, abc.ABC):
    _message: str | None
    _description: str | None

    def __init__(self,
                 *,
                 message: str | None = None,
                 description: str | None = None) -> None:
        self._message = message
        self._description = description

    def __str__(self) -> str:
        message = self.get_message()
        description = self.get_description()

        if not description:
            return message

        return f'{message}: {description}'

    def get_message(self) -> str:
        return self._message or self.get_default_message()

    @abc.abstractmethod
    def get_default_message(self) -> str: ...

    def get_description(self) -> str:
        return self._description or self.get_default_description()

    def get_default_description(self) -> str:
        return ''

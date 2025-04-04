from __future__ import annotations

import abc
from typing import Type

from httpx_oauth.oauth2 import BaseOAuth2


class AbstractOAuthClientFactory(abc.ABC):
    @abc.abstractmethod
    def create(self, *, name: str | None = None) -> BaseOAuth2: ...


class BaseOAuthClientFactory(AbstractOAuthClientFactory):
    def create(self, *, name: str | None = None) -> BaseOAuth2:
        client_class = self.get_client_class()
        client_kwargs = self.get_client_kwargs()

        if name is not None:
            client_kwargs['name'] = name

        return client_class(**client_kwargs)

    @abc.abstractmethod
    def get_client_class(self) -> Type[BaseOAuth2]: ...

    @abc.abstractmethod
    def get_client_kwargs(self) -> dict: ...

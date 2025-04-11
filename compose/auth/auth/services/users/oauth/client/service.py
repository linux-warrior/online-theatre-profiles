from __future__ import annotations

import abc
from collections.abc import Mapping
from typing import Annotated

from fastapi import Depends
from httpx_oauth.oauth2 import BaseOAuth2

from .factories import (
    AbstractOAuthClientFactory,
    GoogleOAuthClientFactory,
    FakeGoogleOAuthClientFactory,
)
from .....core import settings


class AbstractOAuthClientService(abc.ABC):
    @abc.abstractmethod
    def create_client(self, *, provider_name: str) -> BaseOAuth2 | None: ...


class OAuthClientService(AbstractOAuthClientService):
    client_factories: Mapping[str, AbstractOAuthClientFactory]

    def __init__(self, *, client_factories: Mapping[str, AbstractOAuthClientFactory]) -> None:
        self.client_factories = client_factories

    def create_client(self, *, provider_name: str) -> BaseOAuth2 | None:
        client_factory = self.client_factories.get(provider_name)

        if client_factory is None:
            return None

        return client_factory.create(name=provider_name)


async def get_oauth_client_service() -> AbstractOAuthClientService:
    client_factories: Mapping[str, AbstractOAuthClientFactory]

    if settings.test_mode:
        client_factories = {
            'google': FakeGoogleOAuthClientFactory(),
        }
    else:
        client_factories = {
            'google': GoogleOAuthClientFactory(),
        }

    return OAuthClientService(client_factories=client_factories)


OAuthClientServiceDep = Annotated[AbstractOAuthClientService, Depends(get_oauth_client_service)]

from __future__ import annotations


class OAuthServiceException(Exception):
    pass


class InvalidOAuthProvider(OAuthServiceException):
    provider_name: str

    def __init__(self, *, provider_name: str) -> None:
        super().__init__()
        self.provider_name = provider_name

    def __str__(self) -> str:
        return 'Invalid OAuth provider: {provider_name}'.format(
            provider_name=self.provider_name,
        )


class InvalidStateToken(OAuthServiceException):
    state: str

    def __init__(self, *, state: str) -> None:
        super().__init__()
        self.state = state

    def __str__(self) -> str:
        return 'Invalid state token: {state}'.format(
            state=self.state,
        )

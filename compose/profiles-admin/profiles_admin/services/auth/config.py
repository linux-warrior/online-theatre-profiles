from __future__ import annotations

from urllib.parse import urljoin

from django.conf import settings
from pydantic import BaseModel


class AuthConfig(BaseModel):
    scheme: str
    host: str
    port: int

    @property
    def service_url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'

    @property
    def api_url(self) -> str:
        return urljoin(self.service_url, '/auth/api/')

    @property
    def api_v1_url(self) -> str:
        return urljoin(self.api_url, 'v1/')

    def get_login_url(self) -> str:
        return 'jwt/login'

    def get_refresh_url(self) -> str:
        return 'jwt/refresh'

    def get_user_profile_url(self) -> str:
        return f'users/profile'


auth_config = AuthConfig(
    scheme=settings.AUTH_SERVICE['scheme'],
    host=settings.AUTH_SERVICE['host'],
    port=settings.AUTH_SERVICE['port'],
)

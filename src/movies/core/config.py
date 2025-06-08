from __future__ import annotations

import uuid
from urllib.parse import urljoin

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='project_')

    name: str = 'movies'


class OpenTelemetryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='otel_')

    enabled: bool = False
    request_id_required: bool = False
    exporter_otlp_http_endpoint: str | None = None
    service_name: str = 'movies'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 6379
    cache_expire_in_seconds: int = 60 * 5


class ElasticConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 9200

    index_name_films: str = 'films'
    index_name_genres: str = 'genres'
    index_name_persons: str = 'persons'

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000

    @property
    def oauth2_token_url(self) -> str:
        return '/auth/api/v1/jwt/login'

    @property
    def service_url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'

    @property
    def api_url(self) -> str:
        return urljoin(self.service_url, '/auth/api/')

    @property
    def api_v1_url(self) -> str:
        return urljoin(self.api_url, 'v1/')

    def get_user_profile_url(self) -> str:
        return f'users/profile'


class ProfilesConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='profiles_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000

    @property
    def service_url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'

    @property
    def api_url(self) -> str:
        return urljoin(self.service_url, '/profiles/api/')

    @property
    def api_v1_url(self) -> str:
        return urljoin(self.api_url, 'v1/')

    def get_film_rating_url(self, *, film_id: uuid.UUID) -> str:
        return f'ratings/film/{film_id}'

    def get_film_reviews_url(self, *, film_id: uuid.UUID) -> str:
        return f'reviews/film/{film_id}'


class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    otel: OpenTelemetryConfig = OpenTelemetryConfig()
    redis: RedisConfig = RedisConfig()
    elasticsearch: ElasticConfig = ElasticConfig()
    auth: AuthConfig = AuthConfig()
    profiles: ProfilesConfig = ProfilesConfig()


settings = Settings()

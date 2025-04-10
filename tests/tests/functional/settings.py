from __future__ import annotations

from urllib.parse import urljoin

from dotenv import load_dotenv
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

load_dotenv()


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 6379


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 9200

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'


class AuthPostgresqlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_postgresql_')

    database: str = 'auth'
    username: str = 'auth'
    password: str
    host: str = 'localhost'
    port: int = 5432


class AuthRedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_redis_')

    host: str = 'localhost'
    port: int = 6379


class SuperUserSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_superuser_')

    login: str
    password: str


class RateLimiterConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='ratelimiter_')

    times: int = 5
    seconds: int = 60


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='mongo_')

    db: str = ''

    host: str = 'localhost'
    port: int = 27017



class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()
    auth_postgresql: AuthPostgresqlSettings = AuthPostgresqlSettings()  # type: ignore[call-arg]
    auth_redis: AuthRedisConfig = AuthRedisConfig()
    superuser: SuperUserSettings = SuperUserSettings()  # type: ignore[call-arg]
    ratelimiter: RateLimiterConfig = RateLimiterConfig()
    mongo: MongoSettings = MongoSettings()

    movies_url: str = 'http://localhost:8000'
    auth_service_url: str = 'http://localhost:8000'
    ugc_url: str = 'http://localhost:8000/ugc-mongo'
    notification_service_url: str = 'http://localhost:8000/notification'

    @property
    def movies_api_url(self) -> str:
        return urljoin(self.movies_url, '/api/')

    @property
    def movies_api_v1_url(self) -> str:
        return urljoin(self.movies_api_url, 'v1/')

    @property
    def auth_api_url(self) -> str:
        return urljoin(self.auth_service_url, '/auth/api/')

    @property
    def auth_api_v1_url(self) -> str:
        return urljoin(self.auth_api_url, 'v1/')

    @property
    def ugc_api_v1_url(self) -> str:
        return urljoin(self.ugc_url, '/v1/')

    @property
    def url_notification_api_events(self) -> str:
        return urljoin(self.notification_service_url, '/notification/api/v1/events')

    @property
    def url_notification_api_messages(self) -> str:
        return urljoin(self.notification_service_url, '/notification/api/v1/messages')


settings = Settings()

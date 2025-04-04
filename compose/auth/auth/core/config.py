from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    test_mode: bool = False
    secret_key: str = 'SECRET'
    access_jwt_lifetime: int = 60 * 60
    refresh_jwt_lifetime: int = 24 * 60 * 60
    sql_echo: bool = False

    @property
    def oauth2_token_url(self) -> str:
        return '/auth/api/v1/jwt/login'


class OAuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='oauth_')

    google_client_id: str = ''
    google_client_secret: str = ''


class OpenTelemetryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='otel_')

    enabled: bool = False
    request_id_required: bool = False
    exporter_otlp_http_endpoint: str | None = None
    service_name: str = 'auth'


class PostgreSQLConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgresql_')

    host: str = 'localhost'
    port: int = 5432
    database: str
    username: str
    password: str

    @property
    def engine_url(self) -> str:
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 5432


class CacheConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='cache_')

    timeout: int = 60 * 5


class RateLimiterConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='ratelimiter_')

    times: int = 5
    seconds: int = 60


class SentryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='sentry_')

    dsn: str = ''
    enable_sdk: bool = False
    enable_tracing: bool = False
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0


# noinspection PyArgumentList
class Settings(BaseSettings):
    auth: AuthConfig = AuthConfig()
    oauth: OAuthConfig = OAuthConfig()
    postgresql: PostgreSQLConfig = PostgreSQLConfig()  # type: ignore[call-arg]
    redis: RedisConfig = RedisConfig()
    cache: CacheConfig = CacheConfig()
    ratelimiter: RateLimiterConfig = RateLimiterConfig()
    otel: OpenTelemetryConfig = OpenTelemetryConfig()
    sentry: SentryConfig = SentryConfig()

    @property
    def test_mode(self) -> bool:
        return self.auth.test_mode


settings = Settings()

from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class ProfilesConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='profiles_')

    encryption_key: str
    sql_echo: bool = False


class OpenTelemetryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='otel_')

    enabled: bool = False
    request_id_required: bool = False
    exporter_otlp_http_endpoint: str | None = None
    service_name: str = 'profiles'


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


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000

    @property
    def oauth2_token_url(self) -> str:
        return '/auth/api/v1/jwt/login'

    @property
    def user_profile_url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}/auth/api/v1/users/profile'


class Settings(BaseSettings):
    profiles: ProfilesConfig = ProfilesConfig()  # type: ignore[call-arg]
    otel: OpenTelemetryConfig = OpenTelemetryConfig()
    postgresql: PostgreSQLConfig = PostgreSQLConfig()  # type: ignore[call-arg]
    auth: AuthConfig = AuthConfig()


settings = Settings()

from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class ProfilesConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='profiles_')

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


# noinspection PyArgumentList
class Settings(BaseSettings):
    profiles: ProfilesConfig = ProfilesConfig()
    otel: OpenTelemetryConfig = OpenTelemetryConfig()
    postgresql: PostgreSQLConfig = PostgreSQLConfig()  # type: ignore[call-arg]


settings = Settings()

from __future__ import annotations

from dotenv import load_dotenv
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

load_dotenv()


class PostgreSQLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgresql_')

    host: str | None = 'localhost'
    port: int | None = 5432
    database: str
    username: str | None = None
    password: str | None = None

    @property
    def connection_params(self) -> dict:
        return {
            'host': self.host,
            'port': self.port,
            'dbname': self.database,
            'user': self.username,
            'password': self.password,
        }


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    scheme: str = 'http'
    host: str | None = 'localhost'
    port: int | None = 9200

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'


class Settings(BaseSettings):
    postgresql: PostgreSQLSettings = PostgreSQLSettings()  # type: ignore[call-arg]
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()


settings = Settings()

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "password"  # noqa: S105
    db: str = "postgres"

    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="POSTGRES_",
        extra="ignore",
    )


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    password: str = "password"  # noqa: S105
    db: int = 0

    @property
    def dsn(self) -> RedisDsn:
        auth = f":{self.password}@" if self.password else ""
        return RedisDsn(f"redis://{auth}{self.host}:{self.port}/{self.db}")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="REDIS_",
        extra="ignore",
    )


postgres = PostgresSettings()
redis = RedisSettings()

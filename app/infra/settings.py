from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    dsn: PostgresDsn = PostgresDsn("postgresql+asyncpg://postgres:password@localhost:5432/postgres")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="POSTGRES_",
        extra="ignore",
    )


class RedisSettings(BaseSettings):
    dsn: RedisDsn = RedisDsn("redis://:password@localhost:6379/0")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="REDIS_",
        extra="ignore",
    )


postgres = PostgresSettings()
redis = RedisSettings()

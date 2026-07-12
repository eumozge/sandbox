from pydantic_settings import BaseSettings, SettingsConfigDict


class Spimex(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SPIMEX_",
        extra="ignore",
    )
    url: str = ""


spimex = Spimex()


class RabbitMQ(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RABBITMQ_",
        extra="ignore",
    )
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"  # noqa: S105
    mgmt_port: int = 15672


rabbitmq = RabbitMQ()

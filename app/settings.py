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
    password: str = "guest"
    mgmt_port: int = 15672

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


rabbitmq = RabbitMQ()

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

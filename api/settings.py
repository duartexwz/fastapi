from pydantic import Field  # pragma: no cover
from pydantic_settings import BaseSettings, SettingsConfigDict  # pragma: no cover


class Settings(BaseSettings):  # pragma: no cover
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    DATABASE_URL: str = Field(init=False)

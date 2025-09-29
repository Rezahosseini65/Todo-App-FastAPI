from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env")

settings = Setting()
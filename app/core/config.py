from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    DEBUG: bool = True
    SECRET_KEY : str

    model_config = SettingsConfigDict(env_file=".env")

settings = Setting()
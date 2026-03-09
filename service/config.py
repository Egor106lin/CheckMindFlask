from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    VK_CLIENT_ID: str
    VK_CLIENT_SECRET: str
    FRONTEND_URL: str
    JOIN_SECRET: str
    GOOGLE_REDIRECT_URI: str
    VK_REDIRECT_URI: str
    DATABASE_URL: str = 'sqlite:///app.db'
    FLASK_DEBUG: bool
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

ENV = os.getenv('FLASK_ENV')
env_file = '.env.production' if ENV == 'production' else '.env.development'

config = Settings(_env_file=env_file)
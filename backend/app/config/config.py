import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinRelief AI"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Security Settings
    SECRET_KEY: str = "local-development-secret-key-very-secret-12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    
    # MySQL Database Settings
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "finrelief_db"
    
    # Google Gemini Settings
    GEMINI_API_KEY: str = ""

    # Database URL Properties
    @property
    def async_database_url(self) -> str:
        """Returns the async connection string for aiomysql."""
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def sync_database_url(self) -> str:
        """Returns the sync connection string for alembic and other synchronous engines."""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Instantiate the global settings object
settings = Settings()

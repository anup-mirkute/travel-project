from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

# Get PROJECT1 root directory
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Production FastAPI"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Cache
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    FROM_EMAIL: str
    EMAIL_VERIFY_EXPIRE_MINUTES: int = 10

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Settings
    OTP_TYPE: List[str] = ['email_verification', 'phone_verification', 'password_reset']

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True
    )

settings = Settings()

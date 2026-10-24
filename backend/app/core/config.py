from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    frontend_url: str = "http://localhost:5173"
    log_level: str = "INFO"

    @field_validator("jwt_secret")
    @classmethod
    def secret_must_be_long_enough(cls, value: str) -> str:
        # PyJWT warns for HMAC keys shorter than the SHA-256 block size.
        if len(value) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return value


settings = Settings()  # type: ignore[call-arg]

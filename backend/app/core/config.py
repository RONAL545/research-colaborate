from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    database_url: str = "postgresql+psycopg://mvp:mvp@localhost:5432/mvp"
    environment: str = "development"
    jwt_secret: SecretStr = SecretStr("development-only-change-this-secret-32")
    institutional_domains: list[str] = Field(default_factory=lambda: ["unaj.edu.pe"])
    access_token_minutes: int = Field(default=30, ge=1)
    verification_token_minutes: int = Field(default=60, ge=1)

    @model_validator(mode="after")
    def secure_production(self):
        secret = self.jwt_secret.get_secret_value()
        if self.environment != "development" and (
            len(secret) < 32 or secret.startswith("development-")
        ):
            raise ValueError("Configure a strong JWT_SECRET outside development")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

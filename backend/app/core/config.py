"""Typed, environment-backed application settings with safe production defaults."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    """Explicit environments prevent accidental production-like defaults."""

    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Configuration boundary; values are read only from `SHAHAB_` variables."""

    model_config = SettingsConfigDict(
        env_prefix="SHAHAB_",
        case_sensitive=False,
        enable_decoding=False,
    )

    app_name: str = "Shahab Recommendation API"
    environment: AppEnvironment = AppEnvironment.LOCAL
    debug: bool = False
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    # Operational schemas require an approved restricted documentation environment.
    api_docs_include_operations: bool = False
    cors_allowed_origins: tuple[str, ...] = ()
    readiness_token: SecretStr | None = None
    database_url: SecretStr | None = None
    database_pool_size: int = 5
    database_max_overflow: int = 5
    database_connect_timeout_seconds: int = 5
    redis_url: SecretStr | None = None
    # Development OTP works on existing local containers without a newly added env variable.
    # Composition still denies mock access in staging/production, regardless of this flag.
    profile_mock_otp_enabled: bool = True

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
            raise ValueError("log_level must be a standard Python logging level")
        return normalized

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        """Allow an explicit comma-separated local value without permissive defaults."""
        if isinstance(value, str):
            return tuple(item.strip() for item in value.split(",") if item.strip())
        return value

    @property
    def docs_enabled(self) -> bool:
        """Interactive docs are deliberately disabled in production by default."""
        return self.environment is not AppEnvironment.PRODUCTION

    @property
    def redis_url_value(self) -> str | None:
        return self.redis_url.get_secret_value() if self.redis_url else None

    @property
    def database_url_value(self) -> str | None:
        """Expose the database URL only to infrastructure composition code."""
        return self.database_url.get_secret_value() if self.database_url else None


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()

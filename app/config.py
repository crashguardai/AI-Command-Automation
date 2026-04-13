"""Application configuration (thresholds, paths)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load from environment or defaults."""

    model_config = SettingsConfigDict(env_prefix="NCA_", env_file=".env", extra="ignore")

    # Minimum probability to trust the intent classifier (else fallback).
    # Slightly permissive so the model accepts more paraphrases when rules do not fire.
    intent_confidence_threshold: float = 0.28
    # Where audit logs are written.
    log_dir: Path = Path("logs")
    log_file: str = "audit.log"


settings = Settings()

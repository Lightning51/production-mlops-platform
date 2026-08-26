from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Values can be overridden using environment variables.
    """

    app_name: str = "Production MLOps Platform"
    environment: str = "development"

    mlflow_tracking_uri: str = "http://127.0.0.1:5000"

    model_name: str = "customer-churn-model"
    model_version: str = "1"

    model_local_path: str = "ml/models/customer_churn_model.joblib"

    model_load_timeout_seconds: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached application settings instance.
    """

    return Settings()

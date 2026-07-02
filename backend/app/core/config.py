"""
Application configuration.
Loads settings from environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Agriculture Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    # Weather API
    WEATHER_API_KEY: str = ""
    WEATHER_API_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # ML model paths
    DISEASE_MODEL_PATH: str = "./app/ml/artifacts/disease_model.pt"
    YIELD_MODEL_PATH: str = "./app/ml/artifacts/yield_model.pkl"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

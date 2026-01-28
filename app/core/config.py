"""
Core configuration for LearnFlow backend
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # App
    app_name: str = "LearnFlow"
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    # Database - SQLite for local development
    database_url: str = "sqlite:///./learnflow.db"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "learnflow-backend"

    # Authentication settings - simplified approach without JWT
    # Session timeout in minutes
    session_timeout_minutes: int = 1440  # 24 hours

    # Gemini
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_model: str = "gemini-2.5-flash"

    # CORS
    cors_origins: List[str] = Field(default=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "https://learnflow.local",
    ])

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True, extra='allow')


settings = Settings()

"""Application configuration settings."""

from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    All settings can be configured via environment variables or .env file.
    """

    # Application Settings
    app_name: str = Field(default="Smart HR Tool", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # API Settings
    api_prefix: str = Field(default="/api/v1", description="API route prefix")
    cors_origins: list[str] = Field(
        default=["http://localhost:8501"],
        description="Allowed CORS origins"
    )

    # Ollama Configuration (Local AI)
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    ollama_model: str = Field(
        default="deepseek-r1:8b",
        description="Ollama model name"
    )
    ollama_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Ollama generation temperature (0.0-2.0)"
    )
    ollama_max_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Maximum tokens for Ollama generation"
    )

    # Groq Configuration (Cloud AI)
    groq_api_key: str = Field(
        description="Groq API key (required)",
        min_length=10
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model name"
    )
    groq_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Groq generation temperature (0.0-2.0)"
    )
    groq_max_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Maximum tokens for Groq generation"
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        description="API rate limit per minute"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./hrcraft.db",
        description="Database URL (sqlite:///./hrcraft.db for development, postgresql://... for production)"
    )
    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum database connection overflow"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True
    )

    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_key(cls, v: str) -> str:
        """Validate Groq API key format."""
        if not v or not v.startswith("gsk_"):
            raise ValueError("Invalid Groq API key format. Must start with 'gsk_'")
        if len(v) < 20:
            raise ValueError("Groq API key is too short")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Invalid environment. Must be one of {valid_envs}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v_upper

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings singleton
    """
    return Settings()


# Export commonly used settings
__all__ = ["Settings", "get_settings"]

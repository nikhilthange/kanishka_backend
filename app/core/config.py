from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings and Configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "AI-Powered Task Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Environment
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    DEBUG: bool = True

    # Database Configuration (PostgreSQL, MySQL, or fallback SQLite)
    # Examples:
    # PostgreSQL: postgresql+psycopg2://postgres:postgres@localhost:5432/taskdb
    # MySQL: mysql+pymysql://root:password@localhost:3306/taskdb
    # SQLite: sqlite:///./taskmanager.db
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/taskdb",
        description="SQLAlchemy database connection URI (PostgreSQL or MySQL)",
    )

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(
        default="super-secret-kanishka-jwt-key-change-in-production-min-32-chars-long",
        description="Secret key for signing JWT tokens",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # AI Configuration (supports 'gemini', 'openai', 'anthropic', or 'mock')
    AI_PROVIDER: Literal["gemini", "openai", "anthropic", "mock"] = Field(
        default="gemini",
        description="LLM provider: gemini, openai, or anthropic (falls back gracefully to mock if no key)",
    )
    GEMINI_API_KEY: str | None = Field(
        default=None,
        description="Google Gemini API key",
    )
    OPENAI_API_KEY: str | None = Field(
        default=None,
        description="OpenAI API key",
    )
    ANTHROPIC_API_KEY: str | None = Field(
        default=None,
        description="Anthropic Claude API key",
    )
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"


settings = Settings()

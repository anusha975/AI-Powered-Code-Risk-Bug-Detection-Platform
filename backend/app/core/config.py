"""
Application Configuration and Environment Settings.
Loads and validates settings from environment variables or .env file.
"""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.constants import AnalysisMode


class Settings(BaseSettings):
    """Platform global configuration settings."""
    
    # Environment & Info
    APP_NAME: str = "Privacy-Preserving AI Code Security Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server Binding
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    API_PREFIX: str = "/api"
    
    # CORS Origins
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, (list, str)):
            return v
        return []
    
    # Database Settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "code_security_db"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/code_security_db"
    
    # Ingestion Constraints & File Validation
    MAX_FILE_SIZE_BYTES: int = 2_097_152     # 2 MB maximum upload size
    MAX_CODE_LENGTH_CHARS: int = 500_000     # 500,000 characters limit
    TEMP_STORAGE_DIR: str = "temp_ingest"    # Transient isolation directory

    # Privacy & Security Guardrails
    ANALYSIS_MODE: AnalysisMode = AnalysisMode.LOCAL_STATIC_ONLY
    ENFORCE_SECRET_REDACTION: bool = True
    ALLOW_REMOTE_LLM: bool = False
    MAX_SNIPPET_LINE_LIMIT: int = 50

    # Module 6 & 8: Privacy-Aware AI & Local LLM Configuration
    AI_ENABLED: bool = True
    LLM_PROVIDER: str = "mock"              # "mock" (offline test/sim), "external" (OpenAI/cloud API), "local" (Ollama/vLLM/Air-gapped)
    LLM_MODEL_NAME: str = "privacy-guard-llm-v1"
    LLM_API_KEY: Union[str, None] = None
    LLM_API_URL: Union[str, None] = None
    LLM_TIMEOUT_SECONDS: int = 10
    LLM_MAX_CONTEXT_LINES: int = 10         # Maximum context window lines per finding
    LLM_MAX_FINDINGS_TO_EXPLAIN: int = 3    # Top N critical findings to generate AI explanations for

    # Module 8: Private / Local LLM Settings
    LOCAL_LLM_URL: str = "http://127.0.0.1:11434"       # Ollama or local OpenAI-compatible endpoint
    LOCAL_LLM_MODEL: str = "llama3.2:1b"               # e.g., codellama, deepseek-coder:6.7b, qwen2.5-coder:7b
    LOCAL_LLM_API_TYPE: str = "ollama"                 # "ollama" or "openai_compatible"
    LOCAL_LLM_TIMEOUT_SECONDS: int = 15
    LOCAL_LLM_MAX_RETRIES: int = 1

    # Module 12: Authentication, Authorization & Security Audit Settings
    JWT_SECRET_KEY: str = "privacy-guard-zero-leak-jwt-secret-key-2026-production-ready"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 10
    RATE_LIMIT_SCAN_PER_MINUTE: int = 30
    AUTH_REQUIRED: bool = False  # Allows progressive non-breaking access in dev/testing, with strict verification when tokens are supplied

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )


settings = Settings()

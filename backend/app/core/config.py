"""
Configurações centralizadas do sistema
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Configuração do Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App
    app_name: str = "Gerador de Questoes Academicas"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    
    # Database - aceita DATABASE_URL do ambiente
    database_url: str = "postgresql://questgen_user:questgen_pass@localhost:5432/questgen_db"
    
    # Redis (opcional)
    redis_url: str = "redis://localhost:6379/0"
    
    # AI Providers
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_provider: str = "openai"  # openai | gemini | claude
    
    # Upload
    max_file_size_mb: int = 20
    allowed_extensions: str = "pdf,txt,docx"
    upload_dir: str = "/tmp/uploads"
    
    # Generation
    max_questions_per_request: int = 20
    min_content_words: int = 500
    generation_timeout_seconds: int = 120
    
    # JWT
    jwt_secret_key: str = "jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # CORS - inclui GitHub Pages e Render
    cors_origins: str = "http://localhost,http://localhost:80,http://localhost:3000,http://localhost:8080,http://127.0.0.1,https://PedroHeinrichSP.github.io,https://pedroheinrichsp.github.io,https://questgen-backend.onrender.com"
    
    # Open Data Portal
    open_data_api_url: str = "https://dadosabertos.camara.leg.br/api/v2"
    open_data_cache_ttl: int = 3600
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

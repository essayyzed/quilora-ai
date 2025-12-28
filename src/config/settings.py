"""
Quilora Application Settings

Centralized configuration management using Pydantic Settings.
All settings can be overridden via environment variables.
"""

from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # -------------------------------------------------------------------------
    # LLM API Keys
    # -------------------------------------------------------------------------
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    openai_api_key: str = Field(..., description="OpenAI API key (required for embeddings)")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    
    # -------------------------------------------------------------------------
    # LLM Configuration (Tiered Strategy)
    # -------------------------------------------------------------------------
    primary_llm_provider: str = Field(
        default="groq:llama-3.3-70b-versatile",
        description="Primary LLM for most queries (free, fast)"
    )
    fallback_llm_provider: str = Field(
        default="openai:gpt-4o-mini",
        description="Fallback LLM if primary fails"
    )
    premium_llm_provider: str = Field(
        default="anthropic:claude-3-5-sonnet-20240620",
        description="Premium LLM for complex queries"
    )
    
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=1024, ge=1, le=4096)
    llm_streaming: bool = Field(default=True, description="Enable streaming responses")
    
    # -------------------------------------------------------------------------
    # Qdrant Vector Database
    # -------------------------------------------------------------------------
    qdrant_host: str = Field(default="localhost", description="Qdrant server host")
    qdrant_port: int = Field(default=6333, ge=1, le=65535)
    qdrant_collection_name: str = Field(default="documents", description="Qdrant collection name")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant Cloud API key")
    qdrant_url: Optional[str] = Field(default=None, description="Qdrant Cloud URL (overrides host/port)")
    
    # -------------------------------------------------------------------------
    # Embedding Configuration
    # -------------------------------------------------------------------------
    embedding_provider: str = Field(
        default="openai",
        description="Embedding provider: 'openai' or 'sentence-transformers'"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model name"
    )
    embedding_dimension: int = Field(default=1536, ge=128, le=4096)
    
    # -------------------------------------------------------------------------
    # Document Processing
    # -------------------------------------------------------------------------
    chunk_size: int = Field(default=512, ge=128, le=2048, description="Document chunk size in tokens")
    chunk_overlap: int = Field(default=50, ge=0, le=500, description="Overlap between chunks in tokens")
    chunk_separator: str = Field(default="\n\n", description="Separator for splitting documents")
    
    supported_file_types: List[str] = Field(
        default=["pdf", "txt", "md", "docx"],
        description="Supported document file types"
    )
    max_file_size_mb: int = Field(default=10, ge=1, le=100, description="Max upload size in MB")
    
    # -------------------------------------------------------------------------
    # Retrieval Configuration
    # -------------------------------------------------------------------------
    retrieval_top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    min_similarity_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold"
    )
    
    # -------------------------------------------------------------------------
    # FastAPI Application
    # -------------------------------------------------------------------------
    app_name: str = Field(default="Quilora", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    app_description: str = Field(default="Ask your documents anything", description="App description")
    debug: bool = Field(default=False, description="Debug mode")
    
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535)
    
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: 'json' or 'text'")
    log_requests: bool = Field(default=False, description="Log all requests/responses")
    
    # -------------------------------------------------------------------------
    # Storage
    # -------------------------------------------------------------------------
    data_dir: Path = Field(default=Path("./data/documents"), description="Document storage directory")
    
    @field_validator("data_dir", mode="before")
    @classmethod
    def create_data_dir(cls, v):
        """Ensure data directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("supported_file_types", mode="before")
    @classmethod
    def parse_file_types(cls, v):
        """Parse comma-separated file types."""
        if isinstance(v, str):
            return [ft.strip() for ft in v.split(",")]
        return v
    
    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    @property
    def qdrant_connection(self) -> dict:
        """Get Qdrant connection parameters."""
        if self.qdrant_url:
            return {"url": self.qdrant_url, "api_key": self.qdrant_api_key}
        return {"host": self.qdrant_host, "port": self.qdrant_port}
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()
"""Configuration settings for the inference server."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Model settings
    model_name: str = "gpt2"
    model_cache_dir: Optional[str] = None
    max_length: int = 100
    temperature: float = 0.7
    top_p: float = 0.9
    
    # API settings
    api_title: str = "n8n Inference Server"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI-based inference server for text generation"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

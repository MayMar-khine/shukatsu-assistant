"""Settings read from environment variables (or a .env file).

Keeping config in env vars is what makes the app cloud-portable: Render,
AWS Lambda, and your laptop all just set different values.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "mock"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-4-hydrogen"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    cors_origins: str = "http://localhost:5173"

    # Retrieval settings
    chunk_size: int = 400  # characters per chunk
    chunk_overlap: int = 80
    top_k: int = 5  # how many chunks to give the LLM

    # Rate limits for /api/fit and /api/draft (protects the free LLM quota)
    hourly_limit_per_ip: int = 20
    daily_limit: int = 500


settings = Settings()

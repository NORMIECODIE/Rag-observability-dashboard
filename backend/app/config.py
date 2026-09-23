from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = "Gemini_API_KEY"
    qdrant_url: str = "http://localhost:6333"
    database_url: str = "postgresql://user:pass@localhost:5432/ragobs"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
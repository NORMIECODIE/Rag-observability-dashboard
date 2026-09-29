from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = "Gemini_API_KEY"
    mongodb_url: str
    mongodb_database: str
    qdrant_url: str = "http://localhost:6333"
    database_url: str = "postgresql://user:pass@localhost:5432/ragobs"
    
    class Config:
        env_file = ".env"


settings = Settings()
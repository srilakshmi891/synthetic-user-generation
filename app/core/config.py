import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Synthetic User Research Platform"
    API_V1_STR: str = "/api/v1"

    # LLM Provider Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Default Models
    DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"
    DEFAULT_OPENAI_MODEL: str = "gpt-4o"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

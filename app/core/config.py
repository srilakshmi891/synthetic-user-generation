from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Synthetic User Research Platform"
    API_V1_STR: str = "/api/v1"

    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"
    DEFAULT_OPENAI_MODEL: str = "gpt-5.5"
    LLM_PROVIDER: str = "gemini"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

print("Google Key Loaded:", bool(settings.GOOGLE_API_KEY))
print("OpenAI Key Loaded:", bool(settings.OPENAI_API_KEY))
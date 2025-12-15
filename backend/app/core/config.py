from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Video Repurposing API"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    REDIS_URL: str
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    AI_PROVIDER: str = "openai"
    USE_MOCK_AI: bool = False # Default to False, can be overridden by env var

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

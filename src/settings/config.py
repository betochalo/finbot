"""Setting for the Finbot project"""
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Define the variables for the Finbot project"""
    LLM_PROVIDER: str
    MODEL_PROVIDER: str

    OPENAI_API_KEY: str

    EMBEDDINGS_PROVIDER: str
    SENTENCE_TRANSFORMER_MODEL: str

    OPENAI_EMBEDDINGS_MODEL: str

    class Config:
        """Settings"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings():
    """Get cached settings"""
    return Settings()

settings = get_settings()

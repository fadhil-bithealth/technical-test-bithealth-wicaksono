from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Info
    APP_NAME: str
    APP_VERSION: str
    
    # Qdrant / Vector DB Configuration
    QDRANT_URL: str
    QDRANT_COLLECTION_NAME: str
    
    # Model Configuration
    VECTOR_SIZE: int

    # Config ini akan otomatis membaca file bernama ".env" di root folder
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Global instance
settings = Settings()
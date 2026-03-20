import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "CineAI Backend"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-for-dev")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    DEVELOPMENT: bool = os.environ.get("DEVELOPMENT", "false").lower() == "true"
    FRONTEND_URLS: list[str] = os.environ.get("FRONTEND_URLS", "").split(",")
    
    OPENROUTER_API_KEY: str = os.environ.get("API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

settings = Settings()

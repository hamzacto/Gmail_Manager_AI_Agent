from pydantic_settings import BaseSettings
from typing import Optional, List
import os

# Get the absolute path to the backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "AI Email Agent"
    VERSION: str = "1.0.1"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Update file paths using absolute paths
    CLIENT_SECRETS_FILE: str = os.path.join(BASE_DIR, "config", "client_secret.json")
    TOKEN_STORAGE_PATH: str = os.path.join(BASE_DIR, "config", "token.json")
    
    # Google OAuth2 settings with expanded scopes
    GOOGLE_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.insert"
    ]
    
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    
    # Groq AI settings
    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str = "llama-3.2-90b-vision-preview"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 1000
    
    # JWT settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    # Update CORS settings to include Vite's default port
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]
    # Google API settings
    PUBSUB_TOPIC_NAME: str = "projects/langflow-449814/topics/gmail-notifications"
    
    # CORS settings
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = True

settings = Settings() 
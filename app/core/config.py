""" Configuration Management """
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "immigration_chatbot")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_VISION_MODEL: str = "gpt-4o"
    IMAGE_ZOOM: float = 2.0
    MAX_PAGES_TO_PROCESS: int = 10
    OCR_MAX_TOKENS: int = 4000
    MAX_FIELDS_PER_FORM: int = 1000
    CHAT_TEMPERATURE: float = 0.7
    CHAT_MAX_TOKENS: int = 500
    MIN_MESSAGES_FOR_MATCHING: int = 6
    STATE_CHATTING: str = "chatting"
    STATE_FORM_MATCHED: str = "form_matched"
    STATE_AWAITING_CONFIRMATION: str = "awaiting_confirmation"
    STATE_FILLING_FORM: str = "filling_form"
    STATE_COMPLETED: str = "completed"
    CORS_ORIGINS: List[str] = [
        "http://167.172.126.196:3031",  
        "https://immigrationai.app"      
    ]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_FILE_TYPES: List[str] = [".pdf"]
    
    class Config:
        env_file = ".env"

settings = Settings()
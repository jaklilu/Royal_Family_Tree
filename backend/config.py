import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL')
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN') or 'dev-admin-token-change-in-production'
    
    # CORS origins - comma separated
    allowed_origins_str = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5500,http://127.0.0.1:5500')
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_str.split(',')]
    
    # Root person ID (optional, will use oldest base person if not set)
    ROOT_PERSON_ID = os.environ.get('ROOT_PERSON_ID')
    
    # Validate DATABASE_URL is set
    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Please set it in your Render dashboard under Environment Variables."
        )
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


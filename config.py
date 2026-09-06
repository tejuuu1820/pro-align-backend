import os
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pro_align.db")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        # Fix for old Heroku/Render Postgres URIs
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key-change-in-production")
    
    # AI Engine configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # General API configs
    PORT = int(os.getenv("PORT", 5000))

import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campuskey-dev-secret-2025')
    
    # Use PostgreSQL on Render, SQLite locally
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres'):
        # Render provides PostgreSQL URL - fix for SQLAlchemy
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://')
    else:
        # Local development - use SQLite
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///campuskey.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False


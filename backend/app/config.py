import os
from datetime import timedelta

class Config:
    # Get database URL and handle Render's postgres:// prefix
    db_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Gemini AI API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_API_URL = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent')
    
class DevelopmentConfig(Config):
    DEBUG = True
    
    # Override with DEV_DATABASE_URL if explicitly set, otherwise use base config
    dev_url = os.getenv('DEV_DATABASE_URL')
    if dev_url:
        if dev_url.startswith('postgres://'):
            dev_url = dev_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = dev_url

class ProductionConfig(Config):
    DEBUG = False
    
    # Override with PROD_DATABASE_URL if explicitly set, otherwise use base config
    prod_url = os.getenv('PROD_DATABASE_URL')
    if prod_url:
        if prod_url.startswith('postgres://'):
            prod_url = prod_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = prod_url

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

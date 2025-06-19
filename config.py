import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'مفتاح_سري_للتطبيق_افتراضي'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات قاعدة البيانات
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Fix for Railway PostgreSQL URL format
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/employees.db'
    
    # إعدادات AWS
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    
    # إعدادات التطبيق
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///employees.db'

class ProductionConfig(Config):
    DEBUG = False
    
    # Railway specific settings
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Use Railway's provided database URL
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Render specific settings
    elif os.environ.get('RENDER'):
        # Render provides DATABASE_URL in correct format
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
        # Render-specific optimizations
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {'sslmode': 'require'}
        }
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
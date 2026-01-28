import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration - Lấy từ .env
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
    DB_NAME = os.getenv('DB_NAME', 'BTL')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    @classmethod
    def print_config(cls):
        """In cấu hình để debug"""
        print("=" * 50)
        print("DATABASE CONFIGURATION")
        print("=" * 50)
        print(f"Host: {cls.DB_HOST}")
        print(f"Port: {cls.DB_PORT}")
        print(f"User: {cls.DB_USER}")
        print(f"Password: {'*' * len(cls.DB_PASSWORD) if cls.DB_PASSWORD else '(empty)'}")
        print(f"Database: {cls.DB_NAME}")
        print(f"Connection URI: {cls.SQLALCHEMY_DATABASE_URI[:40]}...")
        print("=" * 50)
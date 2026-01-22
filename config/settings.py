"""
Settings aplikasi dari environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Konfigurasi aplikasi"""
    
    # Base Directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'db_jasa_makeup')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key')
    PASSWORD_SALT_ROUNDS = 12
    
    # Application
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    APP_NAME = "Aplikasi Jasa Makeup"
    APP_VERSION = "1.0.0"
    
    # Paths
    REPORTS_DIR = BASE_DIR / 'reports'
    REPORTS_PDF_DIR = REPORTS_DIR / 'pdf'
    REPORTS_EXCEL_DIR = REPORTS_DIR / 'excel'
    LOGS_DIR = BASE_DIR / 'logs'
    ASSETS_DIR = BASE_DIR / 'assets'
    
    @classmethod
    def ensure_directories(cls):
        """Buat direktori yang diperlukan jika belum ada"""
        directories = [
            cls.REPORTS_PDF_DIR,
            cls.REPORTS_EXCEL_DIR,
            cls.LOGS_DIR,
            cls.ASSETS_DIR / 'images'
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
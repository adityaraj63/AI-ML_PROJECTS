"""
Application Configuration Classes
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION-32chars!!")
    WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "true").lower() == "true"

    # Database
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "ai_ticket_db")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

    # Seamless fallback to SQLite for local testing without MySQL
    if DB_PASSWORD:
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(base_dir, 'app.db')}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_SIZE = 10

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")

    # ML / Model
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "app", "ml", "saved_models")
    DATASET_PATH = os.path.join(BASE_DIR, "dataset", "tickets.csv")

    # Pagination
    TICKETS_PER_PAGE = int(os.environ.get("TICKETS_PER_PAGE", 20))

    # Admin seed
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@company.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123456")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

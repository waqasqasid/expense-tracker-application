"""
Application configuration.
Reads sensitive values from environment variables (see .env.example)
and falls back to sane defaults for local development.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by all environments."""

    # --- Core Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'expense_tracker.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- File uploads ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "receipts")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload size

    # --- Pagination ---
    TRANSACTIONS_PER_PAGE = 10

    # --- Flask-WTF / CSRF ---
    WTF_CSRF_ENABLED = True

    # --- Session ---
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # 7 days
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 7


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

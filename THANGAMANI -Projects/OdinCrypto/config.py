import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'odincrypto-super-secret-key-change-in-production-2024')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-odincrypto-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    WTF_CSRF_ENABLED = True

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'odincrypto.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ENCRYPTED_FOLDER = os.path.join(BASE_DIR, 'encrypted')
    DECRYPTED_FOLDER = os.path.join(BASE_DIR, 'decrypted')
    KEYS_FOLDER = os.path.join(BASE_DIR, 'keys')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'docx', 'xlsx', 'zip',
        'png', 'jpg', 'jpeg', 'mp4', 'enc'
    }

    # Session
    SESSION_COOKIE_SECURE = False  # True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

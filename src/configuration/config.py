from src.constants import SECRET_KEY, DATABASE_URL


class Configuration:
    # SESSION
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_NAME = 'session_id'
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    SECRET_KEY = SECRET_KEY

    # DATABASE
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


class TestConfig:
    """Test configuration for Flask."""
    TESTING = True
    LOGIN_DISABLED = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key-test"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # prodis/developis kasutatakse postgres db'd aga testimisel sqlite,
    # siis sql'i päringus oleva RETURNING käsu puhul see sqlite's ei toimi korrektselt.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'isolation_level': 'AUTOCOMMIT'
    }

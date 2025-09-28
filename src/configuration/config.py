class TestConfig:
    """Test configuration for Flask."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    LOGIN_DISABLED = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key-test"

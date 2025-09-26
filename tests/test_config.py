# tests/test_config.py
# tests/test_config.py
import app.security.hashes.argon2  # noqa: F401
from app.config import Config


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    POSTS_PER_PAGE = 3
    SECRET_KEY = "test-secret-key"

    # ------------------------------
    # Security / Hasher
    # ------------------------------
    HASH_VARIANT = "argon2"

    # Argon2 password hasher settings (låga värden för snabb testning)
    ARGON2_TIME_COST = 1
    ARGON2_MEMORY_COST = 51200   # ~50 MB
    ARGON2_PARALLELISM = 2
    ARGON2_HASH_LENGTH = 16
    ARGON2_SALT_LENGTH = 16
    ARGON2_PEPPER = "test-pepper-secret"

    # ------------------------------
    # Password policy
    # ------------------------------
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False

# tests/test_config.py
class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    POSTS_PER_PAGE = 3
    SECRET_KEY = "test-secret-key"

    # Argon2 password hasher settings (lätta värden för testhastighet)
    ARGON2_TIME_COST = 1
    ARGON2_MEMORY_COST = 51200   # default ~ 64 MB
    ARGON2_PARALLELISM = 2
    ARGON2_HASH_LENGTH = 16
    ARGON2_SALT_LENGTH = 16


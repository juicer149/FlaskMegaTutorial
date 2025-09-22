import os
from typing import Optional

base_dir = os.path.abspath(os.path.dirname(__file__))

# Helper function to convert string env values to boolean
def str_to_bool(value: Optional[str], default: bool = False) -> bool:
    """Convert string env values like '1', 'true', 'yes' to boolean."""
    if not value:
        return default
    return value.strip().lower() in ("true", "1", "yes", "y")


class Config:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(base_dir, ".app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # disables event system → less overhead

    # Mail server
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 25))
    MAIL_USE_TLS = str_to_bool(os.environ.get("MAIL_USE_TLS"), default=False)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Admin emails (comma separated list in .env)
    ADMINS = [email.strip() for email in os.environ.get("ADMINS", "").split(",") if email]

    # Pagination
    POSTS_PER_PAGE = int(os.environ.get("POSTS_PER_PAGE", 3))

    # Argon2id password hashing parameters
    ARGON2_TIME_COST = int(os.environ.get("ARGON2_TIME_COST", 8))           # iterations (default: 8)
    ARGON2_MEMORY_COST = int(os.environ.get("ARGON2_MEMORY_COST", 131072))  # KiB (128 MB default)
    ARGON2_PARALLELISM = int(os.environ.get("ARGON2_PARALLELISM", 2))       # threads (default: 2)
    ARGON2_HASH_LENGTH = int(os.environ.get("ARGON2_HASH_LENGTH", 16))      # bytes (default: 16)
    ARGON2_SALT_LENGTH = int(os.environ.get("ARGON2_SALT_LENGTH", 16))      # bytes (default: 16)
    ARGON2_PEPPER = os.environ.get("ARGON2_PEPPER", "")                     # pepper (optional, default: "")

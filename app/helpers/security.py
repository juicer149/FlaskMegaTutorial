# app/helpers/security.py
from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import current_app
import re

from app.helpers.security_policy import PasswordPolicy


# ------------------------------------------------------------------------------
# Password hashing and verification using Argon2id with pepper
# ------------------------------------------------------------------------------

def _get_hasher() -> PasswordHasher:
    """Build a PasswordHasher from Flask config."""
    return PasswordHasher(
        time_cost=current_app.config["ARGON2_TIME_COST"],
        memory_cost=current_app.config["ARGON2_MEMORY_COST"],
        parallelism=current_app.config["ARGON2_PARALLELISM"],
        hash_len=current_app.config["ARGON2_HASH_LENGTH"],
        salt_len=current_app.config["ARGON2_SALT_LENGTH"],
    )


def _with_pepper(password: str) -> str:
    """Append pepper to the password before hashing."""
    pepper = current_app.config.get("ARGON2_PEPPER", "")
    return password + pepper


def hash_password(password: str) -> str:
    """Hash a password with Argon2id and pepper."""
    hasher = _get_hasher()
    return hasher.hash(_with_pepper(password))


def verify_password(stored_hash: Optional[str], password: Optional[str]) -> bool:
    """Verify a password against an Argon2id hash with pepper."""
    if not stored_hash or not password:
        return False
    hasher = _get_hasher()
    try:
        return hasher.verify(stored_hash, _with_pepper(password))
    except VerifyMismatchError:
        return False


# ------------------------------------------------------------------------------
# Password strength validation
# ------------------------------------------------------------------------------

def is_strong_password(password: str, policy: PasswordPolicy) -> None:
    """Raise ValueError if password does not meet policy."""
    if len(password) < policy.min_length:
        raise ValueError(f"Password must be at least {policy.min_length} characters long.")

    if policy.require_upper and not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if policy.require_lower and not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if policy.require_digit and not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    if policy.require_special and not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain at least one special character.")

# app/helpers/security.py
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(stored_hash: Optional[str], password: Optional[str]) -> bool:
    if not stored_hash or not password:
        return False
    return check_password_hash(stored_hash, password)

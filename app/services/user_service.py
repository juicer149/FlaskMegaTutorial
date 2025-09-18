"""
User service layer.

Responsibilities:
    - Implement domain logic specific to users (business rules, policies).
    - Provide helpers for password management, avatars, etc.
    - Act as a factory for creating valid User entities.

Non-responsibilities:
    - Database persistence (handled by repositories).
    - Input validation (handled by forms/DTOs).
    - Application workflows (handled by routes/controllers).

Think of services as the domain brain:
    They express *what rules apply* and *how entities should behave*,
    while staying independent from persistence and UI. This allows
    the same logic to be reused across web, CLI, or API interfaces.
"""

from typing import Optional
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User


# ------------------------------------------------------------
# Domain logic
# ------------------------------------------------------------

def set_password(user: User, password: str) -> None:
    """Hash and set the user's password."""
    if not password:
        raise ValueError("Password cannot be empty.")
    user.password_hash = generate_password_hash(password)


def check_password(user: User, password: Optional[str]) -> bool:
    """Check if the provided password matches the stored hash."""
    if not password or user.password_hash is None:
        return False
    return check_password_hash(user.password_hash, password)


def avatar_url(user: User, size: int = 128) -> str:
    """Generate a Gravatar URL for the user's avatar."""
    email = user.email.lower().encode('utf-8')
    email_hash = md5(email).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s={size}"


def create_user(username: str, email: str, password: str) -> User:
    """
    Factory: Create a new User entity with hashed password.
    (Does not persist to the database.)
    """
    user = User(username=username, email=email)
    set_password(user, password)
    return user

# app/repositories/user_repository.py
"""
User repository.

Responsibilities:
    - Provide an abstraction over database access for User entities.
    - Encapsulate all SQLAlchemy session operations (add, commit, queries).
    - Expose high-level methods like "find_by_username" instead of raw SQL.

Non-responsibilities:
    - Domain logic (e.g. password hashing, avatar generation).
    - Input validation (e.g. required fields, formats, uniqueness rules).
    - Application workflows (e.g. registration, login).

Think of repositories as collection-like interfaces:
    They act as in-memory collections for domain objects, but backed by
    a database. This keeps services and routes free from persistence details
    and makes testing easier (repositories can be mocked or swapped).
"""

from typing import Optional
from app import db
from app.models import User


class UserRepository:
    """Repository for User entities."""

    def add(self, user: User) -> None:
        db.session.add(user)

    def commit(self) -> None:
        db.session.commit()

    def save(self, user: User) -> None:
        """Shortcut for add+commit."""
        self.add(user)
        self.commit()

    def find_by_username(self, username: str) -> Optional[User]:
        return db.session.scalar(
            db.select(User).where(User.username == username)
        )

    def find_by_email(self, email: str) -> Optional[User]:
        return db.session.scalar(
            db.select(User).where(User.email == email)
        )

    def get(self, user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)


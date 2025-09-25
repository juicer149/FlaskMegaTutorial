"""
User service layer (domain logic).

- Enforces business rules (uniqueness, normalization, password handling).
- Coordinates persistence by updating User models and committing.
- Keeps forms thin and models focused on data.

Think of services as: the "domain brain" — forms/UI call them,
models store data, services decide the rules.
"""

import sqlalchemy as sa
from flask import current_app
from app import db
from app.models import User
from app.helpers.validators import check_unique_value
from app.helpers.security import is_strong_password
from app.helpers.security_policy import PasswordPolicy


class UserService:
    # ------------------------------
    # Validation helpers
    # ------------------------------
    @staticmethod
    def is_username_unique(username: str, original: str | None = None) -> bool:
        values = db.session.scalars(sa.select(User.username_canonical)).all()
        return check_unique_value(username, values, original=original)

    @staticmethod
    def is_email_unique(email: str, original: str | None = None) -> bool:
        values = db.session.scalars(sa.select(User.email_canonical)).all()
        return check_unique_value(email, values, original=original)

    @staticmethod
    def _get_password_policy() -> PasswordPolicy:
        """Read password policy from config (centralized here)."""
        return PasswordPolicy(
            min_length=current_app.config.get("PASSWORD_MIN_LENGTH", 8),
            require_upper=current_app.config.get("PASSWORD_REQUIRE_UPPER", True),
            require_lower=current_app.config.get("PASSWORD_REQUIRE_LOWER", True),
            require_digit=current_app.config.get("PASSWORD_REQUIRE_DIGIT", True),
            require_special=current_app.config.get("PASSWORD_REQUIRE_SPECIAL", True),
        )

    @staticmethod
    def validate_password_strength(password: str) -> None:
        """Validate password according to policy. Raises ValueError if weak."""
        policy = UserService._get_password_policy()
        is_strong_password(password, policy)
    # ------------------------------
    # User operations
    # ------------------------------
    @staticmethod
    def register_user(
        username: str | None,
        email: str | None,
        password: str | None,
    ) -> User:
        if not username or not email or not password:
            raise ValueError("Username, email and password are required")

        username = username.strip()
        email = email.strip()

        if not UserService.is_username_unique(username):
            raise ValueError("Username already taken")
        if not UserService.is_email_unique(email):
            raise ValueError("Email already taken")

        # Validate password strength
        UserService.validate_password_strength(password)

        # Create user
        user = User(username, email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_profile(user: User, username: str, about_me: str | None) -> None:
        if not username:
            raise ValueError("Username cannot be empty")

        username = username.strip()

        if not UserService.is_username_unique(username, original=user.username_canonical):
            raise ValueError("Username already taken")

        user.username_display = username
        user.username_canonical = username.lower()
        user.about_me = about_me if about_me else None
        db.session.commit()

    @staticmethod
    def change_password(user: User, new_password: str) -> None:
        UserService.validate_password_strength(new_password)
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def reset_password(user: User, new_password: str) -> None:
        UserService.validate_password_strength(new_password)
        user.set_password(new_password)
        db.session.commit()

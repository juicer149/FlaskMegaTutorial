"""
User service layer (domain logic).

- Enforces business rules (uniqueness, normalization, password handling).
- Coordinates persistence by updating User models and committing.
- Keeps forms thin and models focused on data.

Think of services as: the "domain brain" — forms/UI call them,
models store data, services decide the rules.
"""

import sqlalchemy as sa
from app import db
from app.models import User
from app.helpers.validators import check_unique_value

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

    # ------------------------------
    # User operations
    # ------------------------------
    @staticmethod
    def register_user(
        username: str | None,
        email: str | None,
        password: str | None,
        ) -> User:
        # kan man använda en mask typ som kan ge rätt felmeddelande till route?
        if not username or not email or not password:
            raise ValueError("Username, email and password are required")
        if not UserService.is_username_unique(username):
            raise ValueError("Username already taken")
        if not UserService.is_email_unique(email):
            raise ValueError("Email already taken")

        username = username.strip()
        email = email.strip()
        
        if not UserService.is_username_unique(username):
            raise ValueError("Username already taken")
        if not UserService.is_email_unique(email):
            raise ValueError("Email already taken")

        user = User(username, email)
        user.set_password(password) # om jag har denna här så kan jag ta bort den från modellen eller från services?
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

    # not changed in user model yet
    @staticmethod
    def change_password(user: User, new_password: str) -> None:
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def reset_password(user: User, new_password: str) -> None:
        user.set_password(new_password)
        db.session.commit()


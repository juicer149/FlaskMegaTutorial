"""
In Grindbergs tutorial this file does not exist. Also he made validation in the forms.py file.

He puts it like this:

"
chapter 7:
...

Fixing the Duplicate Username Bug

I have used the username duplication bug for too long. Now that I have showed you how to prepare the application to handle these types of errors, I can go ahead and fix it.

If you recall, the RegistrationForm already implements validation for usernames, but the requirements of the edit form are slightly different. During registration, I need to make sure the username entered in the form does not exist in the database. On the edit profile form I have to do the same check, but with one exception. If the user leaves the original username untouched, then the validation should allow it, since that username is already assigned to that user. Below you can see how I implemented the username validation for this form:

app/forms.py: Validate username in edit profile form.

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')

The implementation is in a custom validation method, but there is an overloaded constructor that accepts the original username as an argument. This username is saved as an instance variable, and checked in the validate_username() method. If the username entered in the form is the same as the original username, then there is no reason to check the database for duplicates.
"
---

First i followed his approach but i made a small deviation by making the validate function as a helper duo to the fact that it felt wrong to have a form depend on a database query.

I now also se that this shouldnt even be in forms.py but rather in a service layer.

So in this file i will create a service/factory layer for user related stuff.

for example this class will contain the validate_unique function for mail and username.
i will also take out some of the things in the user model duo to the fact that it has started to become bloated.

---

The reasoning here is based on separation of concerns. A form belongs to the UI layer
and should only deal with syntactic validation (required fields, correct format, matching values).
Once a validator needs to hit the database or enforce domain rules, it crosses into the domain layer,
and that is where a service/factory becomes the correct home.

By moving uniqueness checks and other business rules into UserService we get:
- Forms that stay lightweight and framework-specific (UI concerns only).
- A User model that focuses on persistence and data representation instead of accumulating logic.
- A clear service layer that centralizes domain rules and makes them reusable across different interfaces
  (HTML forms, REST API, CLI, background jobs).
- Better testability, since service methods can be tested independently of Flask and WTForms.
- Alignment with clean architecture principles: models = data, services = domain logic, forms/views = UI.

I also considered whether forms should call directly into the service for field-level validation,
in order to surface errors nicely in templates. This is a trade-off:
    - Including thin adapters in forms improves UX (field-specific errors).
    - Omitting them keeps forms 100% UI-only but requires routes to map service errors into flash messages.
For now the decision is to keep business logic strictly in the service layer, but adapters could
be reintroduced in forms if field-level error rendering is required later.

This design also allows us to gradually slim down the User model.
Operations like registration, profile updates, password resets and uniqueness checks
will live in UserService, while User remains a clean SQLAlchemy entity.

In short: this refactor moves us closer to a clean, layered architecture
where each part of the system has one responsibility and can evolve independently.
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


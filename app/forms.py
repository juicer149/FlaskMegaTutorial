"""
Flask-WTF/WTForms objects.

Responsibilities:
    - Represent user input from the web layer (e.g. login, registration).
    - Perform basic UI-level validation (not domain logic).
        - e.g. "Field is required", "Email has correct format", "Passwords match".
    - Provide CSRF protection automatically.

Think of forms as a filter between the web layer and the domain layer.

In the long run:
    - In a Domain-Driven Design (DDD) or service-layer approach,
      forms may be replaced by:
        - Pydantic models (API/CLI input validation).
        - Marshmallow schemas (serialization + validation).
        - Dataclasses with validation logic (factories, __post_init__).
    - In that case, the web layer becomes only a thin adapter to the domain layer.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(
                sa.select(User).where(
                    User.username == username.data
                    )
                )
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(
                sa.select(User).where(
                    User.email == email.data
                    )
                )
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

"""
Flask-WTF forms.

Responsibilities:
    - Collect and validate raw input from HTML forms at the UI level.
    - Provide CSRF protection automatically.
    - Enforce only presentation-level rules:
        * Field presence (required fields)
        * Basic formats (email shape, min/max lengths, password match)

Non-responsibilities:
    - Database queries (e.g. uniqueness checks)
    - Domain/business rules (e.g. username policies, password strength)
    - Persistence logic

In this design, forms are a thin adapter between the web layer (HTML) and 
the domain layer (Pydantic DTOs, services, repositories). More complex 
validation and domain logic is handled outside the forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


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


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

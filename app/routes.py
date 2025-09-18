"""
Routes (Flask views).

Responsibilities:
    - Define the web-facing endpoints (@app.route).
    - Act as the application's "controller layer":
        * Receive HTTP requests from the client.
        * Delegate input to forms/DTOs for validation.
        * Call services or repositories for domain logic and persistence.
        * Return an HTTP response (HTML via templates, or JSON for APIs).

Non-responsibilities:
    - Domain logic (belongs in services).
    - Database queries (belongs in repositories).
    - Low-level input validation (belongs in forms/DTOs).

Mental model:
    Think of routes as the entry points into the system — like CLI commands.
    They orchestrate the flow: "take input → call domain → return output",
    while staying thin and free from business rules.
"""
from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from app.services.user_service import set_password, check_password, create_user
from app.repositories.user_repository import UserRepository
from app.helpers.navigation import get_next_page

# Repository instance
user_repo = UserRepository()

# ----------------------------------------------------------
# Global hooks
# ----------------------------------------------------------
@app.before_request
def before_request():
    """ Update last_seen for logged-in users before each request """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------

# Home page route
@app.route('/')
@app.route('/index')
@login_required
def index():
    """ Home page with sample posts """

    posts = [
        { 'author': {'username': 'John'}, 'body': 'Beautiful day in Portland!'},
        {'author': {'username': 'Susan'}, 'body': 'The Avengers movie was so cool!'}
    ]
    return render_template('index.html', title='Home', posts=posts)


# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    """ User login page """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = user_repo.find_by_username(form.username.data) # type: ignore
        if user is None or not check_password(user, form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(get_next_page(default=('user', {'username': user.username})))

    return render_template('login.html', title='Sign In', form=form)


# User logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ User registration route """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        assert form.username.data is not None
        assert form.email.data is not None

        if user_repo.find_by_username(form.username.data):
            flash('Username already taken. Please choose a different one.')
            return redirect(url_for('register'))

        if user_repo.find_by_email(form.email.data):
            flash('Email already registered. Please log in.')
            return redirect(url_for('login'))

        user = create_user(form.username.data, form.email.data, form.password.data) # type: ignore
        user_repo.save(user)
        login_user(user) # Not in book: Log in the user immediately after registering
        flash(f'Welcome {user.username}, your account has been created and are now logged in!')
        return redirect(get_next_page(default=('user', {'username': user.username})))

    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    """ User profile page """
    user = db.first_or_404(
        sa.select(User).where(User.username == username)
    )
        # Dummy posts for now
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username, formdata=request.form or None)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    else:
        print(form.errors)

    return render_template('edit_profile.html', title='Edit Profile', form=form)

# jump to row 64 for the main content
"""
Routes (Flask views).

What it is:
    The "controller" layer in an MVC pattern, defined with @app.route.
Responsibilities:
    - Receive HTTP requests.
    - Delegate to forms, models, or services for logic.
    - Return HTTP responses (HTML via templates, or JSON for APIs).

Think of routes as the Unix process entry point:
    Thin and simple — only translate between the web protocol (HTTP) and Python code.

Example:
    The /login route validates form input, checks credentials through the model,
    and then returns either a rendered template or a redirect.
"""
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit
from datetime import datetime, timezone

from app import app, db
from app.models import User
from app.forms import LoginForm, RegistrationForm, EditProfileForm


# ----------------------------------------------------------
# Helper functions
# Could be in a helper file, but small enough to keep here for now
# ----------------------------------------------------------
def get_next_page(default: str | tuple = 'index') -> str:
    """
    Returns a safe redirect target from ?next= query parameter.
    Falls back to given default endpoint if next is missing or unsafe.

    default can be either:
        - a string: 'index'
        - a tuple: ('user', {'username': 'kalle'})
    """
    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
        if isinstance(default, tuple):
            endpoint, values = default
            next_page = url_for(endpoint, **values)
        else:
            next_page = url_for(default)
    return next_page


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

    # Not used anymore, but keeping it duo to the tutorial
    user = {'username': 'Miguel'}

    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
                sa.select(User).where(User.username == form.username.data)
                )
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        # Not in book, but added to log in the user immediately after registering
        # Made a function to get the next page safely and reused it here
        login_user(user, remember=form.remember_me.data)
        return redirect(get_next_page(default=('user', {'username': user.username})))


    return render_template('login.html', title='Sign In', form=form)


# User logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# User registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data) # type: ignore
        user.set_password(form.password.data) # type: ignore
        db.session.add(user)
        db.session.commit()
        login_user(user) # Not in book: Log in the user immediately after registering
        flash(f'Welcome {user.username}, your account has been created and are now logged in!')
        return redirect(get_next_page(default=('user', {'username': user.username})))

    return render_template('register.html', title='Register', form=form)


# User profile page, the use of <...> indicates a dynamic component
@app.route('/user/<username>')
@login_required
def user(username):
    # creates a query that compares the username in the URL to the username in the database
    # if no user is found, it returns a 404 error page
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
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

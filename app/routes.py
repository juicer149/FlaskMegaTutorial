from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit

from app import app, db
from app.models import User
from app.forms import LoginForm, RegistrationForm


# Could be in a helper file
def get_next_page(default: str = 'index') -> str:
    """
    Returns a safe redirect target from ?next= query parameter.
    Falls back to given default endpoint if next is missing or unsafe.
    """
    next_page = request.args.get('next')
    # netloc protects against open redirects attacks
    if not next_page or urlsplit(next_page).netloc != '':
        next_page = url_for(default)
    return next_page

############################################################
# Routes
############################################################

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
        return redirect(get_next_page())


    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

    
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
        return redirect(get_next_page())

    return render_template('register.html', title='Register', form=form)

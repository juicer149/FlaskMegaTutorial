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
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app import app, db
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.helpers.navigation import get_next_page


# ----------------------------------------------------------
# Global hooks
# ----------------------------------------------------------
@app.before_request
def before_request():
    """Update last_seen for logged-in users before each request"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------


# Home page route
@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for("index"))

    # pagination
    page = request.args.get("page", 1, type=int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template(
            "index.html", 
            title="Home", 
            form=form,
            posts=posts.items, 
            next_url=next_url, 
            prev_url=prev_url
            )



# User login route
@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(
                User.username_canonical == form.username.data.lower()  # type: ignore
            )
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        # Not in book, but added to log in the user immediately after registering
        # Made a function to get the next page safely and reused it here
        login_user(user, remember=form.remember_me.data)
        return redirect(
            get_next_page(default=("user", {"username": user.username_canonical}))
        )

    return render_template(
            "login.html", 
            title="Sign In", 
            form=form
            )


# User logout route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# User registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # safe fallback
        username = form.username.data.strip()  # type: ignore
        email = form.email.data.strip()  # type: ignore

        user = User(username, email)

        user.set_password(form.password.data)  # type: ignore
        db.session.add(user)
        db.session.commit()
        login_user(user)  # Not in book: Log in the user immediately after registering
        flash(f"Welcome {user.username_display}, your account has been created!")
        return redirect(
            get_next_page(default=("user", {"username": user.username_canonical}))
        )

    return render_template(
            "register.html", 
            title="Register", 
            form=form
            )


# User profile page, the use of <...> indicates a dynamic component
@app.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(
        sa.select(User).where(User.username_canonical == username.lower())  # type: ignore
    )
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).where(
            Post.author == user).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = url_for(
            "user", 
            username=user.username_canonical, 
            page=posts.next_num
            ) if posts.has_next else None
    prev_url = url_for(
            "user",
            username=user.username_canonical,
            page=posts.prev_num
            ) if posts.has_prev else None
    form = EmptyForm()
    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form
        )


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username_display)
    if form.validate_on_submit():
        new_username = form.username.data.strip()  # type: ignore
        current_user.username_canonical = new_username.lower()
        current_user.username_display = new_username
        current_user.about_me = form.about_me.data if form.about_me.data else None

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username already taken, please choose a different one.")
            return (
                render_template("edit_profile.html", title="Edit Profile", form=form),
                400,
            )

        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))

    elif request.method == "GET":
        form.username.data = current_user.username_display
        form.about_me.data = current_user.about_me

    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username_canonical == username.lower())
        )

        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("index"))

        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for("user", username=user.username_canonical))

        current_user.follow(user)
        db.session.commit()
        flash(f"You are following {user.username_display}!")
        return redirect(url_for("user", username=user.username_canonical))
    else:
        return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username_canonical == username.lower())
        )

        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("index"))

        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for("user", username=user.username_canonical))

        current_user.unfollow(user)
        db.session.commit()
        flash(f"You have unfollowed {user.username_display}.")
        return redirect(url_for("user", username=user.username_canonical))
    else:
        return redirect(url_for("index"))


@app.route("/explore")
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )

    next_url = url_for("explore", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("explore", page=posts.prev_num) if posts.has_prev else None

    return render_template(
        "index.html",
        title="Explore",
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )

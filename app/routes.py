"""
Routes (Flask views).

What it is:
    The "controller" layer in an MVC pattern, defined with @bp.route.
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

from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app,
    Blueprint,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)
import sqlalchemy as sa
from datetime import datetime, timezone

from app import db
from app.models import User, Post
from app.services.user_service import UserService
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    EmptyForm,
    PostForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)
from app.helpers.navigation import get_next_page
from app.email import send_password_reset_email


# ----------------------------------------------------------
# Blueprint
# ----------------------------------------------------------
bp = Blueprint("main", __name__)


# ----------------------------------------------------------
# Global hooks
# ----------------------------------------------------------
@bp.before_app_request
def before_request():
    """Update last_seen for logged-in users before each request"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------
@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)  # type: ignore
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for("main.index"))

    page = request.args.get("page", 1, type=int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = url_for("main.index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main.index", page=posts.prev_num) if posts.has_prev else None

    return render_template(
        "index.html",
        title="Home",
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(
                User.username_canonical == form.username.data.lower()  # type: ignore
            )
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("main.login"))

        login_user(user, remember=form.remember_me.data)
        return redirect(
            get_next_page(default=("main.user", {"username": user.username_canonical}))
        )

    return render_template("login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = UserService.register_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            login_user(user)
            flash(f"Congratulations, {user.username_display}, you are now a registered user!")
            return redirect(url_for("main.user", username=user.username_canonical))
        except ValueError as e:
            flash(str(e))

    return render_template("register.html", title="Register", form=form)


@bp.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(
        sa.select(User).where(User.username_canonical == username.lower())  # type: ignore
    )
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).where(Post.author == user).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = (
        url_for("main.user", username=user.username_canonical, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("main.user", username=user.username_canonical, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    form = EmptyForm()
    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form,
    )


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username_display)
    if form.validate_on_submit():
        try:
            UserService.update_profile(
                user=current_user,  # type: ignore
                username=form.username.data,  # type: ignore
                about_me=form.about_me.data,
            )
            flash("Your changes have been saved.")
            return redirect(url_for("main.edit_profile"))
        except ValueError as e:
            flash(str(e))
    elif request.method == "GET":
        form.username.data = current_user.username_display
        form.about_me.data = current_user.about_me

    return render_template("edit_profile.html", title="Edit Profile", form=form)


@bp.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username_canonical == username.lower())
        )

        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("main.index"))

        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for("main.user", username=user.username_canonical))

        current_user.follow(user)
        db.session.commit()
        flash(f"You are following {user.username_display}!")
        return redirect(url_for("main.user", username=user.username_canonical))
    else:
        return redirect(url_for("main.index"))


@bp.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username_canonical == username.lower())
        )

        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("main.index"))

        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for("main.user", username=user.username_canonical))

        current_user.unfollow(user)
        db.session.commit()
        flash(f"You have unfollowed {user.username_display}.")
        return redirect(url_for("main.user", username=user.username_canonical))
    else:
        return redirect(url_for("main.index"))


@bp.route("/explore")
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )

    next_url = url_for("main.explore", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main.explore", page=posts.prev_num) if posts.has_prev else None

    return render_template(
        "index.html",
        title="Explore",
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = (form.email.data or "").strip().lower()
        user = db.session.scalar(
            sa.select(User).where(User.email_canonical == email)
        )
        if user:
            send_password_reset_email(user)

        flash("Check your email for the instructions to reset your password")
        return redirect(url_for("main.login"))

    return render_template("reset_password_request.html", title="Reset Password", form=form)


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("main.index"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            UserService.reset_password(user, form.password.data)  # type: ignore
            flash("Your password has been reset.")
            return redirect(url_for("main.login"))
        except ValueError as e:
            flash(str(e))

    return render_template("reset_password.html", form=form)


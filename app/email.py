"""
Email utilities.

Responsibilities:
    - Build and send emails (synchronously or asynchronously).
    - Integrate with Flask-Mail using current_app context.
    - Provide helpers for common email flows (e.g., password reset).
"""

from threading import Thread
from typing import TYPE_CHECKING

from flask import render_template, current_app
from flask_mail import Message

from app import mail

if TYPE_CHECKING:  # for type hints only
    from app.models import User


# ----------------------------------------------------------
# Core email sending
# ----------------------------------------------------------
def send_async_email(app, msg: Message) -> None:
    """Send email inside an application context (used in background thread)."""
    with app.app_context():
        mail.send(msg)


def send_email(
    subject: str,
    sender: str,
    recipients: list[str | tuple[str, str]],
    body: str | None = None,
    html: str | None = None,
) -> None:
    """Build and send an email asynchronously."""
    msg = Message(
        subject=subject,
        sender=sender,
        recipients=recipients,
        body=body,
        html=html,
    )
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg),
    ).start()


# ----------------------------------------------------------
# Application-specific helpers
# ----------------------------------------------------------
def send_password_reset_email(user: "User") -> None:
    """Send a password reset email with a secure token."""
    token = user.get_reset_password_token()
    send_email(
        subject="[MyBlog] Reset Your Password",
        sender=current_app.config["ADMINS"][0],
        recipients=[user.email_canonical],
        body=render_template("email/reset_password.txt", user=user, token=token),
        html=render_template("email/reset_password.html", user=user, token=token),
    )


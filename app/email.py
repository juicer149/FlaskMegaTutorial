from threading import Thread
from typing import TYPE_CHECKING

from flask import render_template, current_app, Flask
from flask_mail import Message

from app import mail, app


if TYPE_CHECKING:  # to avoid type: ignore errors
    from app.models import User


def send_async_email(app: Flask, msg: Message) -> None:
    """Send email inside an application context (used in background thread)."""
    with app.app_context():
        mail.send(msg)


def send_email(
        subject: str, 
        sender: str, 
        recipients: list[str | tuple[str, str]] | None = None,
        body: str | None = None, 
        html: str | None = None,
        )-> None:
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
        args=(current_app._get_current_object(), msg)
        ).start()


def send_password_reset_email(user: "User") -> None:
    """Send a password reset email with a secure token."""
    token = user.get_reset_password_token()
    send_email(
        subject = '[MyBlog] Reset Your Password',
        sender = app.config['ADMINS'][0],
        recipients = [user.email_canonical],
        body = render_template(
            'email/reset_password.txt', user=user, token=token
            ),
        html = render_template(
            'email/reset_password.html', user=user, token=token
            ),
        )

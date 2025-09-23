# app/helpers/tokens.py
from time import time
from typing import Optional
import jwt
from flask import current_app

def generate_reset_token(user_id: int, expires_in: int = 600) -> str:
    """Generate a JWT reset token for a given user id."""
    return jwt.encode(
        {"reset_password": user_id, "exp": time() + expires_in},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )

def verify_reset_token(token: str) -> Optional[int]:
    """Verify JWT reset token, return user id if valid."""
    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
        return payload.get("reset_password")
    except Exception:
        return None


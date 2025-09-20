# app/helpers/avatar.py
from hashlib import md5


def gravatar_url(email: str, size: int) -> str:
    digest = md5(email.lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

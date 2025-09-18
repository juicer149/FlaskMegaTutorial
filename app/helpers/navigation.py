# app/helpers/navigation.py
from urllib.parse import urlsplit
from flask import request, url_for
from typing import Union

def get_next_page(default: Union[str, tuple] = "index") -> str:
    """
    Returns a safe redirect target from ?next= query parameter.
    Falls back to given default endpoint if next is missing or unsafe.

    Args:
        default (str | tuple):
            - A string endpoint, e.g. "index"
            - Or a tuple: ("user", {"username": "kalle"})

    Returns:
        str: A safe URL to redirect the user to.
    """
    next_page = request.args.get("next")
    if not next_page or urlsplit(next_page).netloc != "":
        if isinstance(default, tuple):
            endpoint, values = default
            next_page = url_for(endpoint, **values)
        else:
            next_page = url_for(default)
    return next_page


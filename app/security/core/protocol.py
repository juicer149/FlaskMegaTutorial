# app/security/core/protocol.py
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasherProtocol(Protocol):
    """
    Protocol that all hasher implementations must follow.
    Ensures consistency across Argon2, Bcrypt, etc.
    """

    def __init__(self, policy: object | None = None) -> None: ...

    def hash(self, password: str) -> str: ...

    def verify(self, stored_hash: str, password: str) -> bool: ...

    def __call__(self, password: str) -> str: ...


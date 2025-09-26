# app/security/hashes/argon2.py
import logging
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.security.core import register_hasher
from app.security.core.protocol import HasherProtocol
from app.security.policies.argon2_policy import Argon2Policy

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Password hashing and verification using Argon2id (with optional pepper)
# ------------------------------------------------------------------------------

@register_hasher("argon2")
class Argon2(HasherProtocol):
    """Password hashing and verification with Argon2id."""

    def __init__(self, policy: Argon2Policy | None = None) -> None:
        # If no policy is given, use the defaults from Argon2Policy
        self.policy = policy or Argon2Policy()
        self._hasher = PasswordHasher(
            time_cost=self.policy.time_cost,
            memory_cost=self.policy.memory_cost,
            parallelism=self.policy.parallelism,
            hash_len=self.policy.hash_length,
            salt_len=self.policy.salt_length,
        )

    def _with_pepper(self, password: str) -> str:
        """Append pepper if configured."""
        if self.policy.pepper:
            return password + self.policy.pepper
        return password

    def hash(self, password: str) -> str:
        """Hash a password."""
        if not password:
            raise ValueError("Password cannot be empty")
        return self._hasher.hash(self._with_pepper(password))

    def verify(self, stored_hash: str | None, password: str | None) -> bool:
        """Verify a password against a stored hash."""
        if not stored_hash or not password:
            return False
        try:
            return self._hasher.verify(stored_hash, self._with_pepper(password))
        except VerifyMismatchError:
            return False

    def __call__(self, password: str) -> str:
        """Syntactic sugar: argon("mypassword") == argon.hash("mypassword")."""
        return self.hash(password)

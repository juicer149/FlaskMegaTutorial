# app/security/policies/password_policy.py
from dataclasses import dataclass
import logging
import re

from app.security.exceptions import InvalidPolicyConfig

logger = logging.getLogger(__name__)

# Constants
PASSWORD_MIN_LEN_RECOMMENDED = 12
PASSWORD_MIN_LEN_MAX = 128


@dataclass
class PasswordPolicy:
    """
    Password policy configuration.

    Adjust these settings to enforce your desired password complexity requirements.
    Raises InvalidPolicyConfig if any parameter is unsafe.
    """
    min_length: int = 8
    require_upper: bool = True
    require_lower: bool = True
    require_digit: bool = True
    require_special: bool = True

    def __post_init__(self):
        if self.min_length < 1:
            raise InvalidPolicyConfig("Password min_length must be at least 1")
        if self.min_length > PASSWORD_MIN_LEN_MAX:
            logger.warning(
                f"Password min_length {self.min_length} is unusually high "
                f"(>{PASSWORD_MIN_LEN_MAX}). Ensure this is intentional."
            )
        if self.min_length < PASSWORD_MIN_LEN_RECOMMENDED:
            logger.warning(
                f"Password min_length {self.min_length} is below recommended minimum "
                f"of {PASSWORD_MIN_LEN_RECOMMENDED}. Consider increasing it for better security."
            )

    def validate(self, password: str) -> None:
        """Raise InvalidPolicyConfig if password does not meet the policy."""
        if len(password) < self.min_length:
            raise InvalidPolicyConfig(f"Password must be at least {self.min_length} characters long.")

        if self.require_upper and not re.search(r"[A-Z]", password):
            raise InvalidPolicyConfig("Password must contain at least one uppercase letter.")
        if self.require_lower and not re.search(r"[a-z]", password):
            raise InvalidPolicyConfig("Password must contain at least one lowercase letter.")
        if self.require_digit and not re.search(r"\d", password):
            raise InvalidPolicyConfig("Password must contain at least one digit.")
        if self.require_special and not re.search(r"[^A-Za-z0-9]", password):
            raise InvalidPolicyConfig("Password must contain at least one special character.")

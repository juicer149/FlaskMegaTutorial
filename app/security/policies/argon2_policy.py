# argon2 policy implementation for password hashing
# app/security/policies/argon2_policy.py
from dataclasses import dataclass
import logging

from app.security.exceptions import InvalidPolicyConfig

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Constants (policy thresholds)
# ------------------------------------------------------------------------------

ARGON2_MIN_TIME_COST = 1
ARGON2_MAX_TIME_COST = 20

ARGON2_MIN_MEMORY = 65536      # 64 MiB in KiB
ARGON2_WARN_MEMORY = 131072    # 128 MiB in KiB
ARGON2_MAX_MEMORY = 1048576    # 1 GiB in KiB

ARGON2_MIN_PARALLELISM = 1
ARGON2_MAX_PARALLELISM = 64

ARGON2_MIN_HASH_LENGTH = 16
ARGON2_WARN_HASH_LENGTH = 32

ARGON2_MIN_SALT_LENGTH = 16
ARGON2_MIN_PEPPER_LENGTH = 16


# ------------------------------------------------------------------------------
# Policies
# ------------------------------------------------------------------------------

@dataclass
class Argon2Policy:
    """
    Argon2id hashing configuration.

    Modify these parameters based on your security needs and hardware capabilities.
    Defaults are set to reasonable baseline values, but you should always benchmark
    and calibrate for your environment.

    Recommended baseline (OWASP):
        - time_cost: tuned to ~250ms per hash
        - memory_cost: >= 64 MiB (65536 KiB)
        - hash_length: >= 32 bytes
        - salt_length: >= 16 bytes

    Raises:
        InvalidPolicyConfig: If any parameter is set to a fundamentally invalid value.
    """

    time_cost: int = 6
    memory_cost: int = 102400  # KiB
    parallelism: int = 4
    hash_length: int = 32
    salt_length: int = 16
    pepper: str | None = None

    def __post_init__(self):
        # Hard checks: completely invalid values
        if self.time_cost < ARGON2_MIN_TIME_COST:
            raise InvalidPolicyConfig(f"Argon2 time_cost must be >= {ARGON2_MIN_TIME_COST}")

        if self.parallelism < ARGON2_MIN_PARALLELISM:
            raise InvalidPolicyConfig(f"Argon2 parallelism must be >= {ARGON2_MIN_PARALLELISM}")

        if self.hash_length < ARGON2_MIN_HASH_LENGTH:
            raise InvalidPolicyConfig(f"Argon2 hash_length must be >= {ARGON2_MIN_HASH_LENGTH} bytes")

        if self.salt_length < ARGON2_MIN_SALT_LENGTH:
            raise InvalidPolicyConfig(f"Argon2 salt_length must be >= {ARGON2_MIN_SALT_LENGTH} bytes")

        # Former strict checks: now warnings only
        if self.memory_cost < ARGON2_MIN_MEMORY:
            logger.warning(
                f"Argon2 memory_cost {self.memory_cost} KiB is below recommended minimum "
                f"({ARGON2_MIN_MEMORY} KiB / 64 MiB)."
            )

        # Soft warnings (OWASP guidelines)
        if self.memory_cost < ARGON2_WARN_MEMORY:
            logger.warning(
                f"Argon2 memory_cost {self.memory_cost} KiB is below OWASP recommended baseline "
                f"({ARGON2_WARN_MEMORY} KiB / 128 MiB)."
            )
        if self.hash_length < ARGON2_WARN_HASH_LENGTH:
            logger.warning(
                f"Argon2 hash_length {self.hash_length} is below OWASP recommended baseline "
                f"({ARGON2_WARN_HASH_LENGTH} bytes)."
            )

        # Upper bounds sanity checks
        if self.time_cost > ARGON2_MAX_TIME_COST:
            logger.warning(
                f"Argon2 time_cost {self.time_cost} is very high (> {ARGON2_MAX_TIME_COST}); "
                "ensure this is intentional."
            )
        if self.memory_cost > ARGON2_MAX_MEMORY:
            logger.warning(
                f"Argon2 memory_cost {self.memory_cost} KiB is extremely high "
                f"(> {ARGON2_MAX_MEMORY} KiB). Check your config."
            )
        if self.parallelism > ARGON2_MAX_PARALLELISM:
            logger.warning(
                f"Argon2 parallelism {self.parallelism} is unusually high "
                f"(> {ARGON2_MAX_PARALLELISM}) and may cause instability."
            )

        # Pepper validation
        if self.pepper is not None and not isinstance(self.pepper, str):
            raise InvalidPolicyConfig("Argon2 pepper must be a string if provided")
        if self.pepper and len(self.pepper) < ARGON2_MIN_PEPPER_LENGTH:
            logger.warning(
                f"Argon2 pepper is shorter than {ARGON2_MIN_PEPPER_LENGTH} characters – "
                "consider using a stronger secret."
            )
        if not self.pepper:
            logger.info("No pepper configured for Argon2 (optional, but recommended).")


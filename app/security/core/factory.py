# app/security/core/factory.py
from flask import current_app
from app.security.core.hasher import Hasher
from app.security.policies.password_policy import PasswordPolicy
from app.security.policies.argon2_policy import Argon2Policy


class SecurityFactory:
    """Factory to build Hasher + Policies from app config."""

    @staticmethod
    def get_password_policy() -> PasswordPolicy:
        return PasswordPolicy(
            min_length=current_app.config["PASSWORD_MIN_LENGTH"],
            require_upper=current_app.config["PASSWORD_REQUIRE_UPPER"],
            require_lower=current_app.config["PASSWORD_REQUIRE_LOWER"],
            require_digit=current_app.config["PASSWORD_REQUIRE_DIGIT"],
            require_special=current_app.config["PASSWORD_REQUIRE_SPECIAL"],
        )

    @staticmethod
    def get_argon2_policy() -> Argon2Policy:
        return Argon2Policy(
            time_cost=current_app.config["ARGON2_TIME_COST"],
            memory_cost=current_app.config["ARGON2_MEMORY_COST"],
            parallelism=current_app.config["ARGON2_PARALLELISM"],
            hash_length=current_app.config["ARGON2_HASH_LENGTH"],
            salt_length=current_app.config["ARGON2_SALT_LENGTH"],
            pepper=current_app.config["ARGON2_PEPPER"],
        )

    @staticmethod
    def get_hasher() -> Hasher:
        """Create a Hasher using configured variant + policy."""
        variant = current_app.config.get("HASH_VARIANT", "argon2")
        if variant == "argon2":
            policy = SecurityFactory.get_argon2_policy()
        else:
            raise ValueError(f"Unsupported hash variant: {variant}")
        return Hasher(variant=variant, policy=policy)


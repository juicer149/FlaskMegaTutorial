"""
Custom exceptions for the security module.
"""

class InvalidPolicyConfig(ValueError):
    """Raised when a security policy is configured with unsafe or invalid values."""
    pass

__all__ = ["InvalidPolicyConfig"]

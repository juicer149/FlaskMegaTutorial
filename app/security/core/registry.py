# app/security/core/registry.py
import logging
from typing import Type, Callable

from app.security.core.protocol import HasherProtocol

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Typing
# ------------------------------------------------------------------------------
# Every hasher class must implement HasherProtocol
HasherClass = Type[HasherProtocol]

# Global registry of available hashers
_HASHER_REGISTRY: dict[str, HasherClass] = {}

# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------
def register_hasher(name: str) -> Callable[[Type[HasherProtocol]], Type[HasherProtocol]]:
    """
    Class decorator to register a hasher implementation in the global registry.

    Example:
        @register_hasher("argon2")
        class Argon2Hasher:
            ...
    """
    def decorator(cls: Type[HasherProtocol]) -> Type[HasherProtocol]:
        key = name.lower()
        if key in _HASHER_REGISTRY:
            logger.warning("Hasher '%s' is being overwritten in registry.", key)
        _HASHER_REGISTRY[key] = cls
        logger.debug("Registered hasher: %s -> %s", key, cls.__name__)
        return cls
    return decorator


def get_hasher_class(name: str) -> HasherClass:
    """
    Retrieve a registered hasher class by name.

    Args:
        name: The name used when registering (case-insensitive).

    Returns:
        A hasher class implementing HasherProtocol.

    Raises:
        ValueError: If no hasher with that name is registered.
    """
    key = name.lower()
    if key not in _HASHER_REGISTRY:
        raise ValueError(f"Unsupported hash variant: {name}")
    return _HASHER_REGISTRY[key]


def list_hashers() -> list[str]:
    """Return a list of all registered hasher names."""
    return list(_HASHER_REGISTRY.keys())


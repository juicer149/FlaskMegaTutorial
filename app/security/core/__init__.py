"""
Core security primitives.

This subpackage exposes:
- Hasher (the main hasher interface)
- Registry functions (register_hasher, get_hasher_class, list_hashers)
- HasherProtocol (protocol definition for implementations)
"""

from .hasher import Hasher
from .registry import register_hasher, get_hasher_class, list_hashers
from .protocol import HasherProtocol

__all__ = [
    "Hasher",
    "register_hasher",
    "get_hasher_class",
    "list_hashers",
    "HasherProtocol",
]

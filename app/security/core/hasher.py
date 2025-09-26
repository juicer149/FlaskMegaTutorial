# app/security/core/hasher.py
# app/security/core/hasher.py
import logging
from typing import Any

from app.security.core.registry import get_hasher_class
from app.security.core.protocol import HasherProtocol

logger = logging.getLogger(__name__)


class Hasher:
    """
    Abstraction over password hashing algorithms.
    Dynamically selects implementation from registry.
    """

    def __init__(self, variant: str, policy: Any = None):
        hasher_cls = get_hasher_class(variant)
        self.impl: HasherProtocol = hasher_cls(policy)
        self.variant = variant.lower()
        logger.debug("Hasher initialized with variant=%s", self.variant)

    def hash(self, password: str) -> str:
        return self.impl.hash(password)

    def verify(self, stored_hash: str, password: str) -> bool:
        return self.impl.verify(stored_hash, password)


# app/security/tests/test_hasher.py
import unittest
from app.security.core.hasher import Hasher
from app.security.core.registry import _HASHER_REGISTRY, register_hasher

class DummyHasher:
    def __init__(self, policy=None): ...
    def hash(self, password: str) -> str: return "dummy-hash"
    def verify(self, stored_hash: str, password: str) -> bool: return stored_hash == "dummy-hash"

class HasherTestCase(unittest.TestCase):
    def setUp(self):
        # Spara originalregistret och jobba i en ren kopia
        self._orig_registry = _HASHER_REGISTRY.copy()
        _HASHER_REGISTRY.clear()
        register_hasher("dummy")(DummyHasher)

    def tearDown(self):
        # Återställ originalet så efterföljande tester ser Argon2 igen
        _HASHER_REGISTRY.clear()
        _HASHER_REGISTRY.update(self._orig_registry)

    def test_hash_and_verify(self):
        h = Hasher("dummy")
        hashed = h.hash("password")
        self.assertTrue(h.verify(hashed, "password"))

    def test_invalid_variant_raises(self):
        with self.assertRaises(ValueError):
            Hasher("nonexistent")


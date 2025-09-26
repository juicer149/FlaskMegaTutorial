# app/security/tests/test_registry.py
import unittest
from app.security.core.registry import register_hasher, get_hasher_class, list_hashers, _HASHER_REGISTRY

class DummyHasher:
    def __init__(self, policy=None): ...
    def hash(self, password: str) -> str: return "hashed"
    def verify(self, stored_hash: str, password: str) -> bool: return True

class RegistryTestCase(unittest.TestCase):
    def setUp(self):
        self._orig_registry = _HASHER_REGISTRY.copy()
        _HASHER_REGISTRY.clear()

    def tearDown(self):
        _HASHER_REGISTRY.clear()
        _HASHER_REGISTRY.update(self._orig_registry)

    def test_register_and_get_hasher(self):
        register_hasher("dummy")(DummyHasher)
        cls = get_hasher_class("dummy")
        self.assertIs(cls, DummyHasher)

    def test_list_hashers(self):
        register_hasher("dummy")(DummyHasher)
        self.assertIn("dummy", list_hashers())


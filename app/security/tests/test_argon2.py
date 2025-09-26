# app/security/tests/test_argon2.py
import unittest
from app.security.hashes.argon2 import Argon2
from app.security.policies.argon2_policy import Argon2Policy


class Argon2TestCase(unittest.TestCase):
    def setUp(self):
        # 64 MiB – minsta giltiga (men ger en warning i loggarna)
        self.policy = Argon2Policy(memory_cost=65536)
        self.argon2 = Argon2(self.policy)

    def test_hash_and_verify_success(self):
        password = "ValidPass123!"
        hashed = self.argon2.hash(password)
        self.assertTrue(self.argon2.verify(hashed, password))

    def test_verify_wrong_password_fails(self):
        password = "ValidPass123!"
        hashed = self.argon2.hash(password)
        self.assertFalse(self.argon2.verify(hashed, "WrongPass"))


if __name__ == "__main__":
    unittest.main(verbosity=2)


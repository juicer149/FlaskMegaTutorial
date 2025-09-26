# app/security/tests/test_policies.py
import unittest
from app.security.policies.password_policy import PasswordPolicy
from app.security.policies.argon2_policy import Argon2Policy
from app.security.exceptions import InvalidPolicyConfig


class HappyPathPolicyTestCase(unittest.TestCase):
    def test_password_policy_happy_path(self):
        policy = PasswordPolicy(min_length=16)
        self.assertEqual(policy.min_length, 16)

    def test_password_policy_validate_happy_path(self):
        policy = PasswordPolicy(min_length=8)
        # should not raise
        policy.validate("ValidPass1!")

    def test_argon2_policy_happy_path(self):
        policy = Argon2Policy(
            time_cost=6,
            memory_cost=65536,   # 64 MiB
            parallelism=4,
            hash_length=32,
            salt_length=16,
            pepper="supersecretpepperthatistoolong",
        )
        self.assertEqual(policy.hash_length, 32)
        self.assertIsInstance(policy.pepper, str)


class PasswordPolicyTestCase(unittest.TestCase):
    def test_min_length_too_low_raises(self):
        with self.assertRaises(InvalidPolicyConfig):
            PasswordPolicy(min_length=0)

    def test_min_length_warning(self):
        with self.assertLogs(level="WARNING") as cm:
            PasswordPolicy(min_length=6)
        self.assertTrue(any("below recommended minimum" in msg for msg in cm.output))


class Argon2PolicyTestCase(unittest.TestCase):
    def test_invalid_time_cost_raises(self):
        with self.assertRaises(InvalidPolicyConfig):
            Argon2Policy(time_cost=0)

    def test_invalid_memory_cost_warns(self):
        with self.assertLogs(level="WARNING") as cm:
            Argon2Policy(memory_cost=1024)
        self.assertTrue(any("below recommended minimum" in msg for msg in cm.output))

    def test_invalid_parallelism_raises(self):
        with self.assertRaises(InvalidPolicyConfig):
            Argon2Policy(parallelism=0)

    def test_invalid_hash_length_raises(self):
        with self.assertRaises(InvalidPolicyConfig):
            Argon2Policy(hash_length=8)

    def test_invalid_salt_length_raises(self):
        with self.assertRaises(InvalidPolicyConfig):
            Argon2Policy(salt_length=8)

    def test_soft_warning_memory(self):
        with self.assertLogs(level="WARNING") as cm:
            Argon2Policy(memory_cost=70000)
        self.assertTrue(any("below OWASP recommended baseline" in msg for msg in cm.output))

    def test_pepper_wrong_type_raises(self):
        with self.assertRaises(InvalidPolicyConfig):
            Argon2Policy(pepper=1234)  # type: ignore[arg-type]

    def test_pepper_too_short_warns(self):
        with self.assertLogs(level="WARNING") as cm:
            Argon2Policy(pepper="shortpepper")
        self.assertTrue(any("shorter than" in msg for msg in cm.output))

    def test_no_pepper_logs_info(self):
        with self.assertLogs(level="INFO") as cm:
            Argon2Policy(pepper=None)
        self.assertTrue(any("No pepper configured" in msg for msg in cm.output))


if __name__ == "__main__":
    unittest.main()


import unittest
from app import create_app, db
from app.models import User
from app.services.user_service import UserService
from tests.test_config import TestingConfig


class UserServiceCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user_success(self):
        user = UserService.register_user(
            username="Alice",
            email="alice@example.com",
            password="ValidPass1!",
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.username_display, "Alice")
        self.assertTrue(user.check_password("ValidPass1!"))

    def test_register_user_weak_password(self):
        with self.assertRaises(ValueError) as ctx:
            UserService.register_user("Bob", "bob@example.com", "weak")
        self.assertIn("Password", str(ctx.exception))

    def test_register_user_duplicate_username(self):
        UserService.register_user("Alice", "alice@example.com", "ValidPass1!")
        with self.assertRaises(ValueError) as ctx:
            UserService.register_user("Alice", "other@example.com", "ValidPass1!")
        self.assertIn("Username already taken", str(ctx.exception))

    def test_register_user_duplicate_email(self):
        UserService.register_user("Alice", "alice@example.com", "ValidPass1!")
        with self.assertRaises(ValueError) as ctx:
            UserService.register_user("Bob", "alice@example.com", "ValidPass1!")
        self.assertIn("Email already taken", str(ctx.exception))

    def test_update_profile_success(self):
        user = UserService.register_user("Alice", "alice@example.com", "ValidPass1!")
        UserService.update_profile(user, username="Alicia", about_me="Hello world")
        self.assertEqual(user.username_display, "Alicia")
        self.assertEqual(user.about_me, "Hello world")

    def test_change_password(self):
        user = UserService.register_user("Alice", "alice@example.com", "ValidPass1!")
        UserService.change_password(user, "NewValid1!")
        self.assertTrue(user.check_password("NewValid1!"))

    def test_reset_password(self):
        user = UserService.register_user("Alice", "alice@example.com", "ValidPass1!")
        UserService.reset_password(user, "ResetValid1!")
        self.assertTrue(user.check_password("ResetValid1!"))


if __name__ == "__main__":
    unittest.main(verbosity=2)


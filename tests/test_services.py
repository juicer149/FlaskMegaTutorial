import unittest
from app import app, db
from app.models import User
from app.services.user_service import UserService


class UserServiceCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
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
            password="secret123",
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.username_display, "Alice")
        self.assertTrue(user.check_password("secret123"))

    def test_register_user_duplicate_username(self):
        UserService.register_user("Alice", "alice@example.com", "secret")
        with self.assertRaises(ValueError) as ctx:
            UserService.register_user("Alice", "other@example.com", "secret")
        self.assertIn("Username already taken", str(ctx.exception))

    def test_register_user_duplicate_email(self):
        UserService.register_user("Alice", "alice@example.com", "secret")
        with self.assertRaises(ValueError) as ctx:
            UserService.register_user("Bob", "alice@example.com", "secret")
        self.assertIn("Email already taken", str(ctx.exception))

    def test_update_profile_success(self):
        user = UserService.register_user("Alice", "alice@example.com", "secret")
        UserService.update_profile(user, username="Alicia", about_me="Hello world")
        self.assertEqual(user.username_display, "Alicia")
        self.assertEqual(user.about_me, "Hello world")

    def test_change_password(self):
        user = UserService.register_user("Alice", "alice@example.com", "secret")
        UserService.change_password(user, "newpass")
        self.assertTrue(user.check_password("newpass"))

    def test_reset_password(self):
        user = UserService.register_user("Alice", "alice@example.com", "secret")
        UserService.reset_password(user, "resetpass")
        self.assertTrue(user.check_password("resetpass"))


if __name__ == "__main__":
    unittest.main(verbosity=2)


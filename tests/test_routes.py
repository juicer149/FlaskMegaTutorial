import unittest
from app import create_app, db
from app.models import User
from tests.test_config import TestingConfig
from app.security.core.factory import SecurityFactory


class RoutesCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        self.hasher = SecurityFactory.get_hasher()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register(self, username, email, password, password2=None):
        return self.client.post(
            "/register",
            data={
                "username": username,
                "email": email,
                "password": password,
                "password2": password2 or password,
            },
            follow_redirects=True,
        )

    def login(self, username, password):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        return self.client.get("/logout", follow_redirects=True)

    def test_register_success(self):
        response = self.register("Alice", "alice@example.com", "ValidPass1!")
        self.assertIn(b"Congratulations, Alice", response.data)
        self.assertIsNotNone(
            db.session.scalar(
                db.select(User).where(User.username_canonical == "alice")
            )
        )

    def test_register_duplicate_username(self):
        self.register("Alice", "alice@example.com", "ValidPass1!")
        self.logout()
        response = self.register("Alice", "other@example.com", "ValidPass1!")
        self.assertIn(b"Please use a different username.", response.data)

    def test_register_duplicate_email(self):
        self.register("Alice", "alice@example.com", "ValidPass1!")
        self.logout()
        response = self.register("Bob", "alice@example.com", "ValidPass1!")
        self.assertIn(b"Please use a different email address.", response.data)

    def test_login_success(self):
        u = User(username="Alice", email="alice@example.com")
        u.set_password("ValidPass1!", self.hasher)
        db.session.add(u)
        db.session.commit()

        response = self.login("Alice", "ValidPass1!")
        self.assertIn(b"Home", response.data)

    def test_login_invalid_credentials(self):
        u = User(username="Alice", email="alice@example.com")
        u.set_password("ValidPass1!", self.hasher)
        db.session.add(u)
        db.session.commit()

        response = self.login("Alice", "WrongPass123!")
        self.assertIn(b"Invalid username or password", response.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)


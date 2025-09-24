import unittest
from app import app, db
from app.models import User


class RoutesCase(unittest.TestCase):
    def setUp(self):
        # Setup app context & test client
        self.app_context = app.app_context()
        self.app_context.push()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False  # disable CSRF for tests
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"  # in-memory DB
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register(self, username, email, password, password2=None):
        """Helper for register route"""
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
        """Helper for login route"""
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        """Helper for logout route"""
        return self.client.get("/logout", follow_redirects=True)

    # ----------------------
    # Tests
    # ----------------------

    def test_register_success(self):
        response = self.register("Alice", "alice@example.com", "secret")
        self.assertIn(b"Congratulations, Alice", response.data)
        self.assertIsNotNone(
            db.session.scalar(
                db.select(User).where(User.username_canonical == "alice")
            )
        )

    def test_register_duplicate_username(self):
        self.register("Alice", "alice@example.com", "secret")
        self.logout()  # ensure we are logged out
        response = self.register("Alice", "other@example.com", "secret")
        self.assertIn(b"Please use a different username.", response.data)

    def test_register_duplicate_email(self):
        self.register("Alice", "alice@example.com", "secret")
        self.logout()  # ensure we are logged out
        response = self.register("Bob", "alice@example.com", "secret")
        self.assertIn(b"Please use a different email address.", response.data)

    def test_login_success(self):
        # Create user directly in DB
        u = User(username="Alice", email="alice@example.com")
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()

        response = self.login("Alice", "secret")
        self.assertIn(b"Home", response.data)

    def test_login_invalid_credentials(self):
        # Create user directly in DB
        u = User(username="Alice", email="alice@example.com")
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()

        response = self.login("Alice", "wrongpass")
        self.assertIn(b"Invalid username or password", response.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)

import unittest
import sqlalchemy as sa
from datetime import datetime, timezone, timedelta

from app import create_app, db
from app.models import User, Post
from tests.test_config import TestingConfig


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username="Susan", email="susan@example.com")
        u.set_password("ValidPass1!")
        self.assertFalse(u.check_password("wrongpass"))
        self.assertTrue(u.check_password("ValidPass1!"))

    def test_avatar(self):
        u = User(username="John", email="john@example.com")
        self.assertIn("gravatar.com", u.avatar(128))

    def test_follow(self):
        u1 = User(username="John", email="john@example.com")
        u2 = User(username="Susan", email="susan@example.com")
        db.session.add_all([u1, u2])
        db.session.commit()

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count, 1)
        self.assertEqual(u2.followers_count, 1)

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count, 0)
        self.assertEqual(u2.followers_count, 0)

    def test_follow_posts(self):
        # four users
        u1 = User(username="John", email="john@example.com")
        u2 = User(username="Susan", email="susan@example.com")
        u3 = User(username="Mary", email="mary@example.com")
        u4 = User(username="David", email="david@example.com")
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.now(timezone.utc)
        p1 = Post(body="post from john", author=u1, timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2, timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4, timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()

        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == "__main__":
    unittest.main(verbosity=2)


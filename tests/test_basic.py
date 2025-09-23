# flake8: noqa: E402
import os
os.environ["DATABASE_URL"] = "sqlite://"

from datetime import datetime, timezone, timedelta  # noqa: E402
import unittest
import sqlalchemy as sa
from app import app, db  # noqa: F402
from app.models import User, Post  # noqa: F402

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        app.config["POSTS_PER_PAGE"] = 3  # test settings for pagination
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username="Susan", email="susan@example.com")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))

    def test_avatar(self):
        u = User(username="John", email="john@example.com")
        self.assertEqual(
            u.avatar(128),
            "https://www.gravatar.com/avatar/"
            "d4c74594d841139328695756648b6bd6"
            "?d=identicon&s=128",
        )

    def test_follow(self):
        u1 = User(username="John", email="john@example.com")
        u2 = User(username="Susan", email="susan@example.com")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(followers, [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count, 1)
        self.assertEqual(u2.followers_count, 1)

        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].username_display, "Susan")
        self.assertEqual(u2_followers[0].username_display, "John")

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count, 0)
        self.assertEqual(u2.followers_count, 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username="John", email="john@example.com")
        u2 = User(username="Susan", email="susan@example.com")
        u3 = User(username="Mary", email="mary@example.com")
        u4 = User(username="David", email="david@example.com")
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.now(timezone.utc)
        p1 = Post(
            body="post from john", author=u1, timestamp=now + timedelta(seconds=1)
        )
        p2 = Post(
            body="post from susan", author=u2, timestamp=now + timedelta(seconds=4)
        )
        p3 = Post(
            body="post from mary", author=u3, timestamp=now + timedelta(seconds=3)
        )
        p4 = Post(
            body="post from david", author=u4, timestamp=now + timedelta(seconds=2)
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the following posts of each user
        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

    def test_pagination(self):
        u = User(username="Alice", email="alice@example.com")
        db.session.add(u)
        db.session.commit()

        # skapa 10 poster
        now = datetime.now(timezone.utc)
        for i in range(10):
            p = Post(body=f"post {i}", author=u,
                     timestamp=now + timedelta(seconds=i))
            db.session.add(p)
        db.session.commit()

        # kör en query sorterad nyast först
        query = sa.select(Post).order_by(Post.timestamp.desc())

        # hämta första sidan
        page1 = db.paginate(
            query,
            page=1,
            per_page=app.config["POSTS_PER_PAGE"],
            error_out=False,
        )
        self.assertEqual(len(page1.items), app.config["POSTS_PER_PAGE"])
        self.assertTrue(page1.has_next)
        self.assertFalse(page1.has_prev)

        # hämta andra sidan
        page2 = db.paginate(
            query,
            page=2,
            per_page=app.config["POSTS_PER_PAGE"],
            error_out=False,
        )
        self.assertEqual(len(page2.items), app.config["POSTS_PER_PAGE"])
        self.assertTrue(page2.has_next)
        self.assertTrue(page2.has_prev)

        # sista sidan (ska ha 1 post kvar → 10 % 3 = 1)
        page4 = db.paginate(
            query,
            page=4,
            per_page=app.config["POSTS_PER_PAGE"],
            error_out=False,
        )
        self.assertEqual(len(page4.items), 1)
        self.assertFalse(page4.has_next)
        self.assertTrue(page4.has_prev)


if __name__ == "__main__":
    unittest.main(verbosity=2)

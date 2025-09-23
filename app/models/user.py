"""
User model and related methods.
"""

from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask_login import UserMixin

from app import db, login
from app.helpers.security import hash_password, verify_password
from app.helpers.avatar import gravatar_url
from app.helpers import tokens
from .followers import followers  # import association table


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    username_canonical: orm.Mapped[str] = orm.mapped_column(
        sa.String(64), index=True, unique=True, nullable=False
    )
    username_display: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=False)
    email_canonical: orm.Mapped[str] = orm.mapped_column(
        sa.String(120), index=True, unique=True, nullable=False
    )
    email_display: orm.Mapped[str] = orm.mapped_column(sa.String(120), nullable=False)
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column(
        sa.String(1024), nullable=True
    )
    posts: orm.WriteOnlyMapped["Post"] = orm.relationship(  # type: ignore[name-defined]
        back_populates="author"
    )
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(140))
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    following: orm.WriteOnlyMapped["User"] = orm.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates="followers",
    )
    followers: orm.WriteOnlyMapped["User"] = orm.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates="following",
    )

    def __init__(self, username: str, email: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.username_canonical = username.lower()
        self.username_display = username
        self.email_canonical = email.lower()
        self.email_display = email

    def set_password(self, password: str) -> None:
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = hash_password(password)

    def check_password(self, password: Optional[str]) -> bool:
        return verify_password(self.password_hash, password)

    def get_reset_password_token(self, expires_in: int = 600) -> str:
        return tokens.generate_reset_token(self.id, expires_in)

    @staticmethod
    def verify_reset_password_token(token: str) -> Optional["User"]:
        user_id = tokens.verify_reset_token(token)
        if user_id is None:
            return None
        return db.session.get(User, user_id)

    def avatar(self, size: int) -> str:
        return gravatar_url(self.email_canonical, size)

    def follow(self, user) -> None:
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user) -> None:
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user: "User") -> bool:
        query = sa.select(sa.exists(self.following.select().where(User.id == user.id)))
        return bool(db.session.scalar(query))

    def _relationship_count(self, relationship) -> int:
        count_query = sa.select(sa.func.count()).select_from(
            relationship.select().subquery()
        )
        return int(db.session.scalar(count_query) or 0)

    @property
    def followers_count(self) -> int:
        return self._relationship_count(self.followers)

    @property
    def following_count(self) -> int:
        return self._relationship_count(self.following)

    def following_posts(self):
        # local import to avoid circular import
        from .post import Post

        Author = orm.aliased(User)
        Follower = orm.aliased(User)

        stmt = (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(Follower.id == self.id, Author.id == self.id))
            # .group_by(Post)
            .distinct()
            .order_by(Post.timestamp.desc())
        )
        return stmt

    def __repr__(self) -> str:
        return f"<User {self.username_display}>"


@login.user_loader
def load_user(id: str) -> Optional["User"]:
    return db.session.get(User, int(id))

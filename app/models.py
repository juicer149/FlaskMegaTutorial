"""
SQLAlchemy ORM models.

Responsibilities:
    - Map Python classes to database tables (Object–Relational Mapping).
    - Define columns, indexes, and foreign keys.
    - Provide relationship logic between tables (e.g. user.posts ↔ post.author).
    - May include simple helper methods (e.g. password hashing),
      but ideally business logic belongs in a domain/service layer.

Think of this file as "memory on disk":
    A convenient abstraction over raw SQL for persistence.
"""
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask_login import UserMixin

from app import db, login
from app.helpers.security import hash_password, verify_password
from app.helpers.avatar import gravatar_url


# ------------------------------------------------------------------------------
# Association Tables
# Many-to-Many relationships
# ------------------------------------------------------------------------------

# PK = follower_id + followed_id
followers = sa.Table( "followers", db.metadata,
    sa.Column( 'follower_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True ),
    sa.Column( 'followed_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True ),
    # Diviation from the book: prevent a user from following themselves
    sa.CheckConstraint('follower_id != followed_id', name='no_self_follow')
)


# ------------------------------------------------------------------------------
# ORM Models
# ------------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: orm.Mapped[int] = orm.mapped_column( 
            primary_key=True, autoincrement=True
            ) 
    # Canonical username is stored in lowercase to ensure uniqueness
    username_canonical: orm.Mapped[str] = orm.mapped_column(
            sa.String(64), index=True, unique=True, nullable=False, 
            )
    # Display username retains original casing for UI purposes
    username_display: orm.Mapped[str] = orm.mapped_column(
            sa.String(64), nullable=False
            )
    email_canonical: orm.Mapped[str] = orm.mapped_column(
            sa.String(120), index=True, unique=True, nullable=False,
            )
    email_display: orm.Mapped[str] = orm.mapped_column(
            sa.String(120), nullable=False
            )
    # Optional because it may not be set initially
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column( 
            sa.String(256), nullable=True 
            )
    posts: orm.WriteOnlyMapped['Post'] = orm.relationship( 
            back_populates="author"
            )
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column( 
            sa.String(140)
            )
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
            default=lambda: datetime.now(timezone.utc)
            )
    following: orm.WriteOnlyMapped['User'] = orm.relationship(
            secondary=followers, primaryjoin=( followers.c.follower_id == id ),
            secondaryjoin=( followers.c.followed_id == id ),
            back_populates='followers'
            )
    followers: orm.WriteOnlyMapped['User'] = orm.relationship(
            secondary=followers, primaryjoin=( followers.c.followed_id == id ),
            secondaryjoin=( followers.c.follower_id == id ),
            back_populates='following'
            )

    def __init__(self, username: str, email:str, **kwargs) -> None:
        """ This should be in a a service layer /domain layer ideally """
         # Call the base constructor to handle other fields
        super().__init__(**kwargs)
        self.username_canonical = username.lower()
        self.username_display = username
        self.email_canonical = email.lower()
        self.email_display = email


    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)

    def check_password(self, password: Optional[str]) -> bool:
        return verify_password(self.password_hash, password)

    def avatar(self, size: int) -> str:
        return gravatar_url(self.email_canonical, size)

    def follow(self, user) -> None:
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user) -> None:
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user: "User") -> bool: 
        """ 
        Return True if this user follows the given user.
        Uses EXISTS for efficiency (db can stop at first match)
        In tutorial, they used select() which is less efficient duo to counting all matches
        """
        query = sa.select( sa.exists( self.following.select().where( User.id == user.id )))
        return bool(db.session.scalar(query))

    def _relationship_count(self, relationship) -> int:
        """ Helper to count rows in a dynamic relationship """
        count_query = sa.select(sa.func.count()).select_from(
            relationship.select().subquery()
        )
        return int( db.session.scalar( count_query ) or 0 )

    @property
    def followers_count(self) -> int:
        return self._relationship_count(self.followers)

    @property
    def following_count(self) -> int:
        return self._relationship_count(self.following)

    def following_posts(self):  # -> Select[tuple[Post]]: from sqlalchemy.sql import Select
        Author = orm.aliased(User)
        Follower = orm.aliased(User)

        stmt = (
            sa.select(Post)
            .join(Post.author.of_type(Author))          # Join Post to its author
            .join(Author.followers.of_type(Follower), isouter=True)   # Join Author to its followers
            .where(
                sa.or_(
                    Follower.id == self.id,     # Where follower is this user
                    Author.id == self.id     # Or post is authored by this user
                )
            )
            .group_by(Post)                     # Group by Post to avoid duplicates # type: ignore[arg-type]
            .order_by(Post.timestamp.desc())    # Newest posts first
        )
        return stmt


    def __repr__(self) -> str:
        """ Used f string instead of format that is used in the book """
        return f'<User {self.username_display}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id: orm.Mapped[int] = orm.mapped_column( primary_key=True, autoincrement=True)
    body: orm.Mapped[str] = orm.mapped_column( sa.String(140) )

    timestamp: orm.Mapped[datetime] = orm.mapped_column(
                                    index=True, 
                                    default=lambda: datetime.now(timezone.utc)
                                    ) 

    user_id: orm.Mapped[int] = orm.mapped_column(
                                    sa.ForeignKey(User.id),
                                    index=True,
                                    nullable=False
                                    )
    author: orm.Mapped[ User ] = orm.relationship( back_populates='posts' )
                                    

    def __repr__(self) -> str:
        """ Used f string instead of format that is used in the book """
        return f'<Post {self.body}>'


# Flask-Login user loader callback, used to reload the user object from the user ID stored in the session
# if you have many users, consider caching the users with redis, memcached or SQLAlchemy baked queries / identity map
@login.user_loader
def load_user(id: str) -> Optional[User]:
    return db.session.get(User, int(id))

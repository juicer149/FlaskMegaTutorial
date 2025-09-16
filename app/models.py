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
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5 # For avatar generation
from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # Added auto increment to id column, not necessary but good practice to be explicit
    # The ORMs will usually handle this for you but being explicit is good
    id: orm.Mapped[int] = orm.mapped_column( 
                                    primary_key=True, autoincrement=True
                                    ) 
    username: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(64), index=True, unique=True,
                                    nullable=False
                                    )
    email: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(120), index=True, unique=True
                                    )
    # Optional for now as in the book duo to no auth yet
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column( sa.String(256) )

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(back_populates="author")

    about_me: orm.Mapped[Optional[str]] = orm.mapped_column( sa.String(140) )

    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
                                    default=lambda: datetime.now(timezone.utc)
                                    )


    # Note: set_password and check_password are part of the domain layer not the data layer
    # It is okey to have them here for simple apps, but for more complex hashing strategies
    # or if you want to change the hashing strategy later, consider moving them to a service layer
    def set_password(self, password: str) -> None:
        # Added check to avoid empty passwords also to make linter happy
        # This is not in the book
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)

    # Same here about the domain layer
    def check_password(self, password: Optional[str]) -> bool:
        # If password_hash is None, return False
        # this differs from the book but is safer, and avoids potential errors
        # also it makes the linter happy, also added if not password check
        # to secure if someone passes None manually in shell/cli 
        if not password or self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int) -> str:
        """
        Generate avatar URL using Gravatar service.
        It uses MD5 hash of the user's email to create a unique avatar.
        :param size: Size of the avatar in pixels.
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self) -> str:
        """ Used f string instead of format that is used in the book """
        return f'<User {self.username}>'


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

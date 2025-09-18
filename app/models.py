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



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: orm.Mapped[int] = orm.mapped_column( 
                                    primary_key=True, autoincrement=True
                                    ) 
    # Canonical username is stored in lowercase to ensure uniqueness
    username_canonical: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(64), index=True, unique=True,
                                    nullable=False, 
                                    )
    # Display username retains original casing for UI purposes
    username_display: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(64), nullable=False
                                    )
    email_canonical: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(120), index=True, unique=True,
                                    nullable=False,
                                    )
    email_display: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(120), nullable=False
                                    )
    # Optional because it may not be set initially
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column( 
                                                sa.String(256), nullable=True 
                                                                 )
    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(back_populates="author")
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column( sa.String(140) )
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
                                    default=lambda: datetime.now(timezone.utc)
                                    )

    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)

    def check_password(self, password: Optional[str]) -> bool:
        return verify_password(self.password_hash, password)

    def avatar(self, size: int) -> str:
        return gravatar_url(self.email_canonical, size)

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

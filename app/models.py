"""
SQLAlchemy ORM models.

Responsibilities:
    - Define the persistence schema: map Python classes to database tables.
    - Specify columns, indexes, constraints, and relationships.
    - Provide an object-oriented interface for database rows.

Non-responsibilities:
    - Domain/business logic (e.g. password hashing, uniqueness rules, profile policies).
    - Input validation or transformations.
    - Application workflows.

Think of models as the persistence layer only:
    They describe how entities are stored and related in the database,
    not how they are created, validated, or manipulated in the domain.
"""

from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: orm.Mapped[int] = orm.mapped_column( primary_key=True, autoincrement=True ) 
    username: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(64, collation="NOCASE"), index=True, unique=True,
                                    nullable=False, 
                                    )
    email: orm.Mapped[str] = orm.mapped_column(
                                    sa.String(120), index=True, unique=True
                                    )
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column( sa.String(256) )
    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(back_populates="author")
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column( sa.String(140) )
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
                                    default=lambda: datetime.now(timezone.utc)
                                    )

    def avatar(self, size: int) -> str:
        """ Proxy to service layer for backward compatibility in templates """
        from app.services import user_service
        return user_service.avatar_url(self, size)

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

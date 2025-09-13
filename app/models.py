from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app import db


class User(db.Model):
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
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column( 
                                                                 sa.String(256),
                                                                 )
    # Same as Mapped[List['Post']] but is more compadible with mypy
    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(back_populates="author")

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
    author: orm.Mapped[User] = orm.relationship( back_populates='posts' )
                                    

    def __repr__(self) -> str:
        """ Used f string instead of format that is used in the book """
        return f'<Post {self.body}>'

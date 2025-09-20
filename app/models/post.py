"""
Post model.
"""

from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as orm

from app import db


class Post(db.Model):
    __tablename__ = "posts"

    id: orm.Mapped[int] = orm.mapped_column( primary_key=True, autoincrement=True )
    body: orm.Mapped[str] = orm.mapped_column( sa.String(140) )
    timestamp: orm.Mapped[datetime] = orm.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), index=True, nullable=False
    )
    author: orm.Mapped["User"] = orm.relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post {self.body}>"


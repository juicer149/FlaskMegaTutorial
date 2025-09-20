"""
Association table for many-to-many (User ↔ User (followers)).
"""

import sqlalchemy as sa
from app import db

# PK = follower_id + followed_id
followers = sa.Table(
    "followers",
    db.metadata,
    sa.Column("follower_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("followed_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
    # Prevent a user from following themselves
    sa.CheckConstraint("follower_id != followed_id", name="no_self_follow"),
)

from typing import Annotated
from pydantic import BaseModel, EmailStr, field_validator, \
        StringConstraints as constr
from app.models import User as UserModel
from app import db
import sqlalchemy as sa


class RegistrationData(BaseModel):
    username: Annotated[str, constr(min_length=1, max_length=50)]
    email: EmailStr
    password: Annotated[str, constr(min_length=1, max_length=100)]

    @staticmethod
    def _is_unique(field: str, value: str, msg: str) -> str:
        user = db.session.scalar(
                sa.select(UserModel).where(getattr(UserModel, field) == value)
                )
        if user is not None:
            raise ValueError(msg)
        return value

    @field_validator('username')
    def username_unique(cls, v):
        return cls._is_unique('username', v, 'Username already taken')

    @field_validator('email')
    def email_unique(cls, v):
        return cls._is_unique('email', v, 'Email already registered')


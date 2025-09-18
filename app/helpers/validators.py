import sqlalchemy as sa
from wtforms.validators import ValidationError
from app import db


def validate_unique(field, value_field, original: str | None = None, msg: str = "Value must be unique"):
    """
    Generic uniqueness validator.

    Args:
        field: The WTForms field being validated (e.g. username, email).
        value_field: SQLAlchemy ORM field to check uniqueness against.
        original: Optional original value (for edit forms).
        msg: Custom error message.
    """
    canonical = field.data.lower()

    if original and canonical == original.lower():
        return  # unchanged → ok

    exists = db.session.scalar(
        sa.select(value_field).where(value_field == canonical)
    )
    if exists:
        raise ValidationError(msg)


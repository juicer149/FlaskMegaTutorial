# app/helpers/validators.py
from collections.abc import Sequence

def check_unique_value(
    value: str, 
    existing_values: Sequence[str], 
    original: str | None = None
    ) -> bool:
    """
    Check if a value is unique among a given list of canonical values.

    Args:
        value: The string to check.
        existing_values: A list of canonical strings to check against.
        original: Optional original value (for edit forms).
    Returns:
        True if unique, False otherwise.
    """
    canonical = value.lower()
    if original and canonical == original.lower():
        return True
    return canonical not in (v.lower() for v in existing_values)

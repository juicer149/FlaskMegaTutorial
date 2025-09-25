# app/helpers/security_policy.py
from dataclasses import dataclass

@dataclass
class PasswordPolicy:
    min_length: int = 8
    require_upper: bool = True
    require_lower: bool = True
    require_digit: bool = True
    require_special: bool = True

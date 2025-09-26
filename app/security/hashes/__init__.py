"""
Hasher implementations registry loader.
All hashers are imported here so they self-register via @register_hasher.
"""

# Import all algorithms here so they register themselves
from . import argon2

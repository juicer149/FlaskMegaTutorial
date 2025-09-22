from abc import ABC, abstractmethod


PASSWORD = "abc123"


class Hasher(ABC):
    """Abstract base class for password hashing configs."""

    @abstractmethod
    def hash_once(self, password: str = PASSWORD) -> str: ...
    
    @abstractmethod
    def verify_once(self, password: str, hashed: str) -> bool: ...
    
    @property
    @abstractmethod
    def label(self) -> str: ...


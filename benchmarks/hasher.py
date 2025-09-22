from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
import base64

from .hasher_base import Hasher, PASSWORD


class PBKDF2Config(Hasher):
    def __init__(self, iterations: int):
        self.iterations = iterations

    def hash_once(self, password: str = PASSWORD) -> str:
        return generate_password_hash(password, method=f'pbkdf2:sha256:{self.iterations}')

    def verify_once(self, password: str, hashed: str) -> bool:
        return check_password_hash(hashed, password)

    @property
    def label(self) -> str:
        return f"PBKDF2 (iter={self.iterations})"


class BcryptConfig(Hasher):
    def __init__(self, rounds: int):
        self.rounds = rounds

    def hash_once(self, password: str = PASSWORD) -> str:
        hashed_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=self.rounds))
        return base64.b64encode(hashed_bytes).decode("utf-8")

    def verify_once(self, password: str, hashed: str) -> bool:
        hashed_bytes = base64.b64decode(hashed.encode("utf-8"))
        return bcrypt.checkpw(password.encode(), hashed_bytes)

    @property
    def label(self) -> str:
        return f"bcrypt (rounds={self.rounds})"


class Argon2Config(Hasher):
    def __init__(self, time_cost: int, memory_cost: int, parallelism: int, label: str = ""):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self._label = label or f"t={time_cost}, m={memory_cost}, p={parallelism}"
        self.hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
        )

    def hash_once(self, password: str = PASSWORD) -> str:
        return self.hasher.hash(password)

    def verify_once(self, password: str, hashed: str) -> bool:
        try:
            return self.hasher.verify(hashed, password)
        except VerifyMismatchError:
            return False

    @property
    def label(self) -> str:
        return f"argon2id ({self._label})"


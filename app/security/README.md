# Security Module

A modular, extensible security framework for password policies and password hashing.  
Designed for use in web applications (e.g. Flask), but reusable as a standalone package.

---

## Features

- **Policies** (`app/security/policies/`)
  - `PasswordPolicy`: Enforces password complexity (length, digits, symbols, etc.).
  - `Argon2Policy`: Configures Argon2id parameters (time, memory, parallelism, hash length, salt length, optional pepper).
  - Strong invalid config checks (`InvalidPolicyConfig`) and soft warnings via `logging`.

- **Hashes** (`app/security/hashes/`)
  - `Argon2`: Secure password hashing with Argon2id.
  - Supports optional pepper.
  - Implements `hash(password)` and `verify(stored_hash, password)`.

- **Core** (`app/security/core/`)
  - `Protocol`: Defines a consistent interface (`HasherProtocol`) for all hashers.
  - `Registry`: Global registry of hashers via `@register_hasher("argon2")`.
  - `Hasher`: Wrapper that dynamically loads a registered hasher.
  - `SecurityFactory`: Creates `Hasher` + policies directly from Flask config.

- **Extensibility**
  - Add new hashers (e.g., Bcrypt, PBKDF2, Scrypt) by implementing the protocol and registering via `@register_hasher("bcrypt")`.
  - Policies are independent dataclasses and can be swapped per algorithm.

---

## Directory Structure

app/security/
├── init.py # Public exports + auto-register Argon2
├── core/ # Core abstractions
│ ├── factory.py # SecurityFactory (load from Flask config)
│ ├── hasher.py # Hasher wrapper
│ ├── protocol.py # HasherProtocol
│ └── registry.py # Global registry
├── hashes/ # Hashing implementations
│ ├── init.py # Auto-imports Argon2 → registers into registry
│ └── argon2.py # Argon2 implementation
├── policies/ # Policies
│ ├── init.py
│ ├── argon2_policy.py
│ └── password_policy.py
├── exceptions.py # Custom exceptions
└── tests/ # Unit tests (self-contained, isolated registry)


---

## Usage

### 1. Password Policies

```python
from app.security.policies.password_policy import PasswordPolicy
from app.security.exceptions import InvalidPolicyConfig

policy = PasswordPolicy(min_length=12)
policy.validate("ValidPass123!")  # ✅ OK
policy.validate("short")          # ❌ raises InvalidPolicyConfig
```
```python
from app.security.policies.argon2_policy import Argon2Policy

argon_policy = Argon2Policy(
    time_cost=6,
    memory_cost=262144,  # 256 MiB
    parallelism=4,
    hash_length=32,
    salt_length=16,
    pepper="supersecretpepper"
)
```
### 2. Hashing with Argon2 directly
```python
from app.security.hashes.argon2 import Argon2
from app.security.policies.argon2_policy import Argon2Policy

argon2 = Argon2(Argon2Policy())
hashed = argon2.hash("MyStrongPass!")
argon2.verify(hashed, "MyStrongPass!")  # ✅ True
argon2.verify(hashed, "WrongPass")      # ❌ False
```

### 3. Using the Hasher abstraction
```python
from app.security.core.hasher import Hasher
from app.security.policies.argon2_policy import Argon2Policy

hasher = Hasher(variant="argon2", policy=Argon2Policy())
hashed = hasher.hash("MyStrongPass!")
print(hasher.verify(hashed, "MyStrongPass!"))  # ✅ True
```

#### Adding a New Hasher

1 - Implement the protocol (hash, verify, __init__(policy)).

2- Register with the registry:
```python
from app.security.core.registry import register_hasher

@register_hasher("bcrypt")
class BcryptHasher:
    def __init__(self, policy=None): ...
    def hash(self, password: str) -> str: ...
    def verify(self, stored_hash: str, password: str) -> bool: ...
```
3 - Use dynamically:
```python
hasher = Hasher(variant="bcrypt", policy=SomeBcryptPolicy())
```

Developer Guide
1. Integrating with User Model

Use SecurityFactory instead of binding to a specific hasher:
```python
from flask_login import UserMixin
from app import db
from app.security.core.factory import SecurityFactory

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024), nullable=True)

    def set_password(self, password: str) -> None:
        hasher = SecurityFactory.get_hasher()
        self.password_hash = hasher.hash(password)

    def check_password(self, password: str) -> bool:
        hasher = SecurityFactory.get_hasher()
        return hasher.verify(self.password_hash, password)
```

2. Config and Environment Variables

.env (example):

HASH_VARIANT=argon2
ARGON2_TIME_COST=6
ARGON2_MEMORY_COST=131072
ARGON2_PARALLELISM=4
ARGON2_HASH_LENGTH=32
ARGON2_SALT_LENGTH=16
ARGON2_PEPPER=supersecretpepper

PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPER=True
PASSWORD_REQUIRE_LOWER=True
PASSWORD_REQUIRE_DIGIT=True
PASSWORD_REQUIRE_SPECIAL=True


app/config.py:
```python    
import os

class Config:
    HASH_VARIANT = os.getenv("HASH_VARIANT", "argon2")
    ARGON2_TIME_COST = int(os.getenv("ARGON2_TIME_COST", 6))
    ARGON2_MEMORY_COST = int(os.getenv("ARGON2_MEMORY_COST", 131072))
    ARGON2_PARALLELISM = int(os.getenv("ARGON2_PARALLELISM", 4))
    ARGON2_HASH_LENGTH = int(os.getenv("ARGON2_HASH_LENGTH", 32))
    ARGON2_SALT_LENGTH = int(os.getenv("ARGON2_SALT_LENGTH", 16))
    ARGON2_PEPPER = os.getenv("ARGON2_PEPPER", "")

    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", 12))
    PASSWORD_REQUIRE_UPPER = os.getenv("PASSWORD_REQUIRE_UPPER", "true").lower() == "true"
    PASSWORD_REQUIRE_LOWER = os.getenv("PASSWORD_REQUIRE_LOWER", "true").lower() == "true"
    PASSWORD_REQUIRE_DIGIT = os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true"
    PASSWORD_REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
```

3. Example Service Layer Usage
```python    
from app.security.core.factory import SecurityFactory
from app.helpers.exceptions import InvalidPolicyConfig
from app.models import User, db

class UserService:
    @staticmethod
    def register_user(username: str, email: str, password: str) -> User:
        # Validate password
        policy = SecurityFactory.get_password_policy()
        policy.validate(password)

        user = User(username=username, email=email)
        hasher = SecurityFactory.get_hasher()
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user
```

✅ Hashing algorithm & policies are configurable via .env.
✅ User model + services stay clean and independent of crypto details.
✅ Tests isolate registry state → no cross-test contamination.

ToDo:
- Add more hashers (Bcrypt, PBKDF2, Scrypt).
- Move my bencharmks here.
- Add to benchmarks to save settings for desired hashing time/memory to policies.

# Flask Mega Tutorial Project

This project follows [Miguel Grinberg's Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and serves as my structured introduction to **Flask** and modern **full-stack web development**.

> This is a **learning project**. It is not intended for production use, but I try to structure it as if it were – with version control, testing, CI, and code quality checks.

A huge thanks to Miguel Grinberg for providing such a comprehensive and approachable resource.

---

## Purpose

Until recently, most of my programming work involved “raw code” — writing scripts in `nvim`, running them in the terminal, and querying data with SQL (MySQL).
Frameworks, templating engines, ORMs, and deployment tools are **new territory** for me.

This project is my way of building solid knowledge in **modern Python web development**.

---

## Learning Objectives

* **Flask** – Application structure, routing, views, request lifecycle.
* **Blueprints** – Orginicing routes into modular units (bp) instead of a monolithic app.routes.
* **Jinja2** – Dynamic HTML templating.
* **HTML/CSS** – Frontend basics for styling and layout.
* **Database integration** – Using SQLAlchemy ORM (from raw SQL background).
* **User authentication** – Sessions, logins, and password hashing.
* **Password security** – Using Argon2id, environment-based tuning, and password strength policy.
* **Testing** – Unit tests with `unittest`.
* **Code quality** – Linting (`flake8`), type-checking (`mypy`), formatting (`black`).
* **Git & GitHub** – Branching, commits, pull requests, and CI/CD workflows.
* **Deployment (future)** – Containerization (Docker) and deploying to a service like Heroku.

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/juicer149/FlaskMegaTutorial.git
cd FlaskMegaTutorial
````

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
make install
```

### 4. Set environment variables

Copy the example file and adjust if needed:

```bash
cp .env.example .env
```

### 5. Run the app

```bash
make run
```

App will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Password Hashing (Argon2id)

This project uses **Argon2id** for password hashing, following [OWASP recommendations](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
Each hash includes a unique **salt** (generated automatically) and a global secret **pepper** (defined in `.env`).

You can configure Argon2id parameters in `.env`:

# Argon2id password hashing parameters
ARGON2_TIME_COST=8
ARGON2_MEMORY_COST=131072   # KiB (128 MB)
ARGON2_PARALLELISM=2
ARGON2_HASH_LENGTH=32
ARGON2_SALT_LENGTH=16
ARGON2_PEPPER=your-secret-pepper-here

### Why Argon2id?

* **Memory hardness** → defends against GPU and ASIC cracking.
* **Configurable cost factors** → balance between security and performance.
* **Pepper** → extra protection if the database is compromised.

---

## Password Strength Policy

In addition to hashing, a password strength policy is enforced at registration and password reset.
The rules are defined in app/helpers/security_policy.py using a dataclass, and configured via .env.

Example .env section:
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGIT=True
PASSWORD_REQUIRE_SPECIAL=True

future enhancements could include:
PASSWORD_DISALLOW_COMMON=True
PASSWORD_DISALLOW_PWNED=True

## Why this matters?

* Prevents weak passwords that are easily guessable or crackable.
* Centralized policy makes it easy to tune requirements as needed.
* Enforced at both service layer and UI layer (forms.py).


## Development Workflow

Common commands are managed via the `Makefile`:

| Command                | Description                                     |
| ---------------------- | ----------------------------------------------- |
| `make run`             | Run the Flask development server                |
| `make install`         | Install dependencies from `requirements.txt`    |
| `make test`            | Run all unit tests (`unittest`)                 |
| `make lint`            | Run linting with `flake8`                       |
| `make typecheck`       | Run static type checking with `mypy`            |
| `make format`          | Auto-format code with `black`                   |
| `make check`           | Run lint + typecheck + tests (CI mirror)        |
| `make reset-db`        | Reset database and run initial migration        |
| `make bench-profiles`  | Run password hashing benchmarks (fixed configs) |
| `make bench-calibrate` | Calibrate hashing cost to \~250ms               |

---

## Continuous Integration

The project uses **GitHub Actions** for CI/CD.
Every push and pull request triggers the workflow in `.github/workflows/ci.yml`:

* Install dependencies
* Run **flake8** (linting)
* Run **mypy** (type-checking)
* Run **unittest** (test suite)

This ensures that code is consistent and functional before merging.

---

## Project Structure

```text
.
├── .env.example       # Example environment variables (copy to .env for local dev)
├── .github/workflows  # GitHub Actions CI/CD pipelines
├── .gitignore         # Ignore rules for Git
├── Makefile           # Developer commands (run, test, lint, etc.)
├── NOTES.MD           # Personal notes and learning log
├── README.md          # Project overview (this file)
├── app/               # Main Flask application package
│   ├── __init__.py    # App factory, extensions (db, login, migrate)
│   ├── errors.py      # Error handlers (404, 500)
│   ├── forms.py       # Flask-WTF forms (UI adapters, no business logic)
│   ├── helpers/       # Utility functions (security, validators, avatar, navigation)
│   ├── models/        # SQLAlchemy models (User, Post, Followers)
│   ├── routes.py      # Flask routes (controllers, thin entry points)
│   ├── services/      # Service layer (domain logic: user registration, profile updates, password reset, validation, etc.)
│   └── security/               # Modular security framework
│       ├── __init__.py
│       ├── core/               # Factory, protocol, registry
│       ├── hashes/             # Hashing implementations (Argon2, etc.)
│       ├── policies/           # Password and algorithm policies
│       ├── exceptions.py
│       └── benchmarks/         # Benchmarks & calibration tools (will move the old one here)
│   └── templates/     # Jinja2 templates (HTML views)
├── benchmarks/        # Password hashing benchmarks & calibration (legacy, will move to app/security/benchmarks/)
├── config.py          # App configuration via environment variables
├── instance/          # Instance-specific files (e.g., SQLite dev DB)
│   └── app.db
├── migrations/        # Alembic migration scripts
│   └── versions/      # Auto-generated migration versions
├── requirements.txt   # Python dependencies
├── setup.cfg          # Linter and tool configuration (flake8, mypy, black)
└── tests/             # Test suite (unit + integration tests, organized by layer)
    ├── test_models.py
    ├── test_routes.py
    └── test_services.py
```

Layered responsibilities

- routes/ → Controllers. Thin translation from HTTP → service calls → HTTP response.

- forms.py → Presentation layer. WTForms only handles UI validation (required fields, matching passwords). Domain validation is delegated to services.

- services/ → Domain logic. Centralized rules for registration, uniqueness checks, password strength, profile updates, etc. 

- models/ → Persistence. Defines entities, relationships, and database schema. Business logic is minimized.

- helpers/ → Pure functions and utilities (hashing, avatars, validators). Reusable without Flask context.

- templates/ → Views. Jinja2 HTML templates for rendering.

- This separation keeps controllers thin, models clean, and domain rules centralized in services. It aligns with clean architecture principles and makes the codebase easier to test and maintain.

---

## Notes

See [NOTES.md](NOTES.MD) for a detailed log of what I’ve learned, decisions I’ve made, and experiments I’ve tried along the way.

```

---

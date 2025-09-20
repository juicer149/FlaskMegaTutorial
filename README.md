# Flask Mega Tutorial Project

This project follows [Miguel Grinberg's Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and serves as my structured introduction to **Flask** and modern **full-stack web development**.

> ⚠️ This is a **learning project**. It is not intended for production use, but I try to structure it as if it were – with version control, testing, CI, and code quality checks.

A huge thanks to Miguel Grinberg for providing such a comprehensive and approachable resource.

---

## 🎯 Purpose

Until recently, most of my programming work involved “raw code” — writing scripts in `nvim`, running them in the terminal, and querying data with SQL (MySQL).
Frameworks, templating engines, ORMs, and deployment tools are **new territory** for me.

This project is my way of building solid knowledge in **modern Python web development**.

---

## Learning Objectives

* **Flask** – Application structure, routing, views, request lifecycle.
* **Jinja2** – Dynamic HTML templating.
* **HTML/CSS** – Frontend basics for styling and layout.
* **Database integration** – Using SQLAlchemy ORM (from raw SQL background).
* **User authentication** – Sessions, logins, and password hashing.
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
```

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

## Development Workflow

Common commands are managed via the `Makefile`:

| Command          | Description                                  |
| ---------------- | -------------------------------------------- |
| `make run`       | Run the Flask development server             |
| `make install`   | Install dependencies from `requirements.txt` |
| `make test`      | Run all unit tests (`unittest`)              |
| `make lint`      | Run linting with `flake8`                    |
| `make typecheck` | Run static type checking with `mypy`         |
| `make format`    | Auto-format code with `black`                |
| `make check`     | Run lint + typecheck + tests (CI mirror)     |
| `make reset-db`  | Reset database and run initial migration     |

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
│   ├── forms.py       # Flask-WTF forms
│   ├── helpers/       # Utility functions (security, validators, avatar, navigation)
│   ├── models/        # SQLAlchemy models (User, Post, Followers)
│   ├── routes.py      # Flask routes (controllers)
│   └── templates/     # Jinja2 templates (HTML)
├── config.py          # App configuration via environment variables
├── instance/          # Instance-specific files (e.g., SQLite dev DB)
│   └── app.db
├── migrations/        # Alembic migration scripts
│   └── versions/      # Auto-generated migration versions
├── requirements.txt   # Python dependencies
├── setup.cfg          # Linter and tool configuration (flake8, mypy, black)
└── tests.py           # Unit tests (unittest)
```

---

## Notes

See [NOTES.md](NOTES.MD) for a detailed log of what I’ve learned, decisions I’ve made, and experiments I’ve tried along the way.

---

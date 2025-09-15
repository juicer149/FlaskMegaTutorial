## Flask Mega Tutorial Project

This project follows [Miguel Grinberg's Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world), and serves as my hands-on introduction to Flask and full-stack web development.

A big thank you to Miguel Grinberg for creating such a comprehensive and approachable resource for free.

### Purpose

Until now, my programming work has mostly involved writing "raw code" — using `nvim`, running scripts via terminal, and handling data manually with SQL (MySQL). Frameworks, templating engines, ORMs, and deployment tools are all new territory for me.

Through this project, I aim to build structured knowledge in modern web development using Python and Flask.

---

### Learning Objectives

* **Flask** – Application structure, routing, views, and request handling.
* **Jinja2** – Templating and rendering dynamic HTML.
* **HTML/CSS** – Frontend basics to style and structure pages.
* **Database integration** – Using SQLAlchemy or another ORM to abstract database logic (coming from raw SQL background).
* **User authentication** – Managing users, logins, and sessions.
* **Deployment** – Likely on Heroku or similar service.
* **Docker** – Containerizing the app for consistency across environments.
* **Git & GitHub** – Improving my workflow and understanding of version control and collaboration.

---

### Project Status

I will update this README as I progress through each tutorial part and deepen my understanding.

---

### Notes for myself that documents my learning journey

#### 1.
Environment variables with `.env` and python-dotenv

The tutorial uses `flask run` with `.flaskenv` for automatic environment loading.  
Since I prefer a Makefile workflow (`make run` → `python run.py`), I added explicit loading with **python-dotenv**:

# app/__init__.py
from dotenv import load_dotenv
load_dotenv()

Now all sensitive config values (like SECRET_KEY) live in a .env file at the project root.

Key insight:
This separation makes it easier to manage environments and keeps the Makefile approach clean and flexible.

#### 2.
Shell context shortcuts

The tutorial uses a separate microblog.py file to define the Flask shell context.
Instead, I defined it directly in app/__init__.py with @app.shell_context_processor:

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "session": db.session, "User": User, "Post": Post, "sa": sa, "orm": orm}

Now when I run flask shell, I instantly get access to:

- db & session
- User & Post models
- sqlalchemy (sa) and ORM (orm)

Key insight:
This eliminates boilerplate and makes interactive exploration smoother.

#### 3.
Resetting migrations in development

I ran into Alembic revision mismatches while experimenting.
The fastest way to recover (in development, where data isn’t preserved) is:

$ rm x.db                # delete the SQLite database
$ rm -rf migrations/     # delete migration scripts
$ flask db init
$ flask db migrate -m "Initial migration"
$ flask db upgrade

Key insight:
In dev, it’s often simpler to reset both the DB and migrations than to debug Alembic conflicts.
In production, of course, this approach would not be safe.


#### 4.
One important takeaway for me has been the distinction between **SQLAlchemy Core** and the **ORM**.  
I first encountered this in *Talk Python to Me* podcast, episode #5: *SQLAlchemy and Data Access in Python* with Mike Bayer (the creator of SQLAlchemy and Alembic).  

- **Core** is the foundation. It provides a SQL expression language and table abstractions (`Table`, `Column`, `ForeignKey`). With Core, you build queries directly against tables and rows, much like writing SQL but with Python objects. This is powerful, explicit, and often better for reporting, ETL, or scripts.
- **ORM** builds on top of Core. It maps Python classes to tables and lets me work with rows as objects (`User`, `Post`). It introduces relationships (`user.posts ↔ post.author`) for natural object navigation, but still compiles down to Core queries under the hood.

What I learned:
- **Foreign keys** are strictly a database construct — they enforce referential integrity in SQL.  
- **relationship()** and **back_populates** live only in the ORM layer — they don’t affect the schema, but make the Python code more natural.  

So the Core gives correctness and raw power, while the ORM gives productivity and readability. Both are essential — Core guarantees integrity, ORM makes day-to-day development smoother.

This clarified why both are necessary:  
Foreign keys guarantee correctness in the database, while ORM relationships improve readability and developer ergonomics in Python.

**Naming conventions:**
- At the SQL level, it’s best practice to use clear, conventional names for keys, e.g. `user_id`, `author_fk`, `post_id`. This keeps the schema unambiguous and easy to query with raw SQL.
- At the ORM level, you can use more semantic names for relationships, e.g. `author` instead of `user`, `owner`, or `customer`. This makes the Python code read more naturally, e.g. `post.author.username`.

#### 5.
User registration, login flow, and safe redirects

In the tutorial, after a new user registers, they are redirected to the login page and must log in manually.  
I changed this so that a new user is **automatically logged in immediately after registration**.  

To make the redirect logic safer and more reusable, I also introduced a small helper function `get_next_page()`:

```python
def get_next_page(default: str = "index") -> str:
    """
    Returns a safe redirect target from ?next= query parameter.
    Falls back to given default endpoint if next is missing or unsafe.
    """
    next_page = request.args.get("next")
    if not next_page or urlsplit(next_page).netloc != "":
        next_page = url_for(default)
    return next_page
```

This helper prevents open redirect attacks (by checking netloc) and keeps the code DRY, since both /login and /register reuse it.

Result:

- New users are logged in immediately after registering.

- Both login and registration flows redirect users safely to either their original destination (?next=) or back to /index.

- The user experience is smoother, and the redirect logic is centralized and secure.


#### 6.
Flask-Login integration

Flask-Login expects user objects to provide certain methods.  
Instead of writing them myself, I use `UserMixin`, which plugs in sensible defaults:

- `is_authenticated` – True if the user has valid credentials.  
- `is_active` – True unless the account is deactivated.  
- `is_anonymous` – False for real users, True for anonymous visitors.  
- `get_id()` – Returns the user’s unique ID (as a string).

By inheriting from `UserMixin`, my `User` class automatically satisfies Flask-Login’s requirements.

Setup looks like this:
# app/__init__.py
login = LoginManager(app)

# app/models.py
class User(UserMixin, db.Model):
    ...

Flask-Login also gives decorators that simplify route protection:

- @login_required → force login before accessing a view.

- @fresh_login_required → require a recent login (useful for sensitive actions).

- @anonymous_user_required → only allow access if the user is logged out.

- @user_passes_test → custom access checks.

Key insight:
Flask-Login is database-agnostic — it doesn’t care if I use SQLAlchemy, raw SQL, or something else.
All it needs is a user object with the expected interface. SQLAlchemy just makes it smoother.


#### 7.
Password hashing experiments (beyond the tutorial)

The tutorial uses Werkzeug’s `generate_password_hash()` (PBKDF2 by default).  
I want to branch off and experiment with alternative approaches to better understand the security tradeoffs:

- **Plaintext passwords** (deliberately insecure) – to see why this is dangerous and how easily they can be stolen/cracked.
- **Werkzeug PBKDF2 (default)** – current setup from the tutorial.
- **Argon2** – a modern, memory-hard algorithm, strong against GPU/ASIC cracking.
- **bcrypt / scrypt** – to compare speed, memory usage, and resistance to brute-force.
- **Salting & peppering** – adding per-user salts and an application-wide secret (pepper) for extra security.

**Why:**  
- To build intuition about the *security vs usability tradeoffs* in password storage.  
- To practice **Git branching for experiments**, keeping insecure vs secure implementations isolated.  
- To simulate attacks (e.g. with hashcat or MITM tools like Evilginx) and observe how different hashing strategies behave.

This will help me deepen my understanding of practical security and strengthen my workflow for exploratory coding.


#### 8.
Forms, validation, and the bridge to Domain-Driven Design

Flask-WTF (and WTForms) provides convenient integration between HTML forms, validation, and Flask routes.  
In this tutorial, `forms.py` holds classes like `LoginForm` and `RegistrationForm` that encapsulate input fields, validation rules, and CSRF protection. This works well for small/medium Flask projects where validation happens close to the web layer.

But while building this, I realized an important point for future projects that use **Domain-Driven Design (DDD)**:

- In a DDD setup, I would not tie validation and domain rules to the web layer (WTForms).  
- Instead, I could define domain models as **frozen dataclasses with slots**, e.g.:

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class User:
    username: str
    email: str
    password_hash: str


A factory (or service) would handle:

- Creating valid User objects from raw input (API, CLI, or DB).
- Applying parsing, normalization, and domain-specific validation.
- Enforcing invariants at the domain level (not just at the form/Flask level).

This would create a clean separation:

- Web layer (Flask forms & routes): UI concerns, request/response handling.
- Domain layer (dataclasses + factories): business rules, validation, invariants.
- Infrastructure (SQLAlchemy models): persistence, mapping to/from the DB.

Alternative: Using Pydantic models

Instead of dataclasses, I could also use Pydantic (especially v2, which builds on pydantic-core in Rust).
Pydantic models give me automatic validation, parsing, and type enforcement:
from pydantic import BaseModel, EmailStr, constr

class UserModel(BaseModel):
    username: constr(min_length=3, max_length=64)
    email: EmailStr
    password: str

# Example:
user = UserModel(username="kalle", email="kalle@example.com", password="qwerty")

Benefits of Pydantic:

- Built-in validators for types like EmailStr.
- Custom validation methods with @validator.
- Works great as DTOs between web, domain, and persistence layers.
- Already widely used in modern frameworks (e.g. FastAPI).

With Pydantic, I could skip WTForms entirely and validate user input at the API/domain layer, then feed it into either factories or ORMs.

Key insight:
WTForms is great for Flask templates, but long-term, domain models (dataclasses or Pydantic) should own validation and invariants.
The web layer should only translate requests into domain objects, and the ORM should only persist them.
That way, the domain is portable, testable, and independent of frameworks.

In future projects, I want to experiment with replacing WTForms entirely using Pydantic or dataclass-based factories, keeping the Flask layer thin and pushing invariants into the domain.

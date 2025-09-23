# Learning journal

---

## Appendix: Learning Map

This appendix provides a quick overview of the insights documented in this file.
Each numbered section links directly to the detailed notes below.

1. [**Environment variables**](#1-environment-variables-with-env-and-python-dotenv) – Using `.env` and `python-dotenv` to keep config clean and secure.

2. [**Shell context shortcuts**](#2-shell-context-shortcuts) – Preloading `db`, `User`, `Post`, and SQLAlchemy helpers into the Flask shell.

3. [**Resetting migrations**](#3-resetting-migrations-in-development) – Safely resetting Alembic + SQLite during development.

4. [**Core vs ORM**](#4-one-important-takeaway-for-me-has-been-the-distinction-between-sqlalchemy-core-and-the-orm) – Distinguishing SQLAlchemy Core (low-level SQL) and ORM (object mapping).

5. [**Login flow improvements**](#5-user-registration-login-flow-and-safe-redirects) – Auto-login after registration and safe redirects with `get_next_page()`.

6. [**Flask-Login**](#6-flask-login-integration) – Integration with `UserMixin` and decorators for route protection.

7. [**Password hashing experiments**](#7-password-hashing-experiments-beyond-the-tutorial) – Trying different algorithms (PBKDF2, Argon2, bcrypt, scrypt) to explore tradeoffs.

8. [**Forms vs Domain validation**](#8-forms-validation-and-the-bridge-to-domain-driven-design) – Moving validation rules from Flask-WTF to Pydantic/dataclasses for a DDD approach.

9. [**Edit Profile feature**](#9-implemented-an-edit-profile-feature) – Building `/edit_profile` with Flask-WTF, CSRF protection, and pre-populated forms.

10. [**Jinja sub-templates**](#10-discovered-jinja-sub-templates) – DRY principle applied to UI with `_post.html`.

11. [**User activity tracking**](#11-experimented-with-user-activity-indicators) – Updating `last_seen` and experimenting with formatting timestamps.

12. [**Project structure reflections**](#12-reflections-on-project-structure) – Clarifying MVC roles (`routes`, `forms`, `models`, `templates`).

13. [**Error handling**](#11-error-handling-in-flask) – Custom 404/500 templates and how debug mode affects them.

14. [**Email debugging**](#12-email-error-reporting-with-aiosmtpd) – Using `aiosmtpd` for safe local SMTP testing.

15. [**Logging**](#13-logging-with-rotating-file-handlers) – Setting up rotating file handlers for persistent error logs.

16. [**Fixing duplicate usernames**](#14-fixing-duplicate-usernames) – Handling `UNIQUE` constraint violations with better validation and collation.

17. [**Database resets**](#15-database-resets-in-development) – Automating resets with `make reset-db`.

18. [**Canonical vs Display fields**](#18-canonical-vs-display-fields-for-username-and-email) – Split `username`/`email` into canonical (lowercased, unique) and display (user-facing) fields.

19. [**Reusable validators**](#19-extracting-reusable-validators-into-helpers) – Moved repetitive uniqueness checks into `helpers/validators.py` to DRY up forms.

20. [**Extracted model helpers into reusable modules**](#20-extracted-model-helpers-into-reusable-modules) – Moved password hashing, password verification, and avatar generation into `helpers/`.

21. [**Many-to-many relationships**](#21-many-to-many-relationships-core-vs-orm) – Deciding between Core and ORM for association tables.  

22. [**Check constraints in association tables**](#22-check-constraints-and-idempotency-in-followers-table) – Preventing self-follows and thoughts on idempotency.  

23. [**Using @property for model helpers**](#23-using-property-for-cleaner-model-apis) – Cleaner access for counts and simple derived values.  

24. [**Password hashing benchmarks**](#24-password-hashing-benchmarks-and-calibration) – Running calibration and profiling of PBKDF2, bcrypt, and Argon2id.

25. [**Migrating to Argon2id with pepper**](#25-migrating-to-argon2id-with-pepper) – Switching from Werkzeug’s PBKDF2 to Argon2id with environment-based configuration.

26. [**Email support with Flask-Mail**](#26-email-support-with-flask-mail) – Using `Mail` and `Message` to send plain + HTML emails.

27. [**Alternatives to JWT for reset tokens**](#27-alternatives-to-jwt-for-reset-tokens) – Exploring `itsdangerous`, DB-backed tokens, and why I picked JWT.

28. [**Debugging issues with email links**](#28-debugging-issues-with-email-links) – Pitfalls when copying reset links from debug SMTP output.

---


#### 1. Environment variables with .env and python-dotenv

The tutorial uses flask run with .flaskenv for automatic environment loading.  
Since I prefer a Makefile workflow (make run → python run.py), I added explicit loading with **python-dotenv**:

# app/__init__.py
from dotenv import load_dotenv
load_dotenv()

Now all sensitive config values (like SECRET_KEY) live in a .env file at the project root.

Key insight:
This separation makes it easier to manage environments and keeps the Makefile approach clean and flexible.

---


#### 2. Shell context shortcuts

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

---


#### 3. Resetting migrations in development

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

---


#### 4. One important takeaway for me has been the distinction between SQLAlchemy Core and the ORM

One important takeaway for me has been the distinction between **SQLAlchemy Core** and the **ORM**.  
I first encountered this in *Talk Python to Me* podcast, episode #5: *SQLAlchemy and Data Access in Python* with Mike Bayer (the creator of SQLAlchemy and Alembic).  

- **Core** is the foundation. It provides a SQL expression language and table abstractions (Table, Column, ForeignKey). With Core, you build queries directly against tables and rows, much like writing SQL but with Python objects. This is powerful, explicit, and often better for reporting, ETL, or scripts.
- **ORM** builds on top of Core. It maps Python classes to tables and lets me work with rows as objects (User, Post). It introduces relationships (user.posts ↔ post.author) for natural object navigation, but still compiles down to Core queries under the hood.

What I learned:
- **Foreign keys** are strictly a database construct — they enforce referential integrity in SQL.  
- **relationship()** and **back_populates** live only in the ORM layer — they don’t affect the schema, but make the Python code more natural.  

So the Core gives correctness and raw power, while the ORM gives productivity and readability. Both are essential — Core guarantees integrity, ORM makes day-to-day development smoother.

This clarified why both are necessary:  
Foreign keys guarantee correctness in the database, while ORM relationships improve readability and developer ergonomics in Python.

**Naming conventions:**
- At the SQL level, it’s best practice to use clear, conventional names for keys, e.g. user_id, author_fk, post_id. This keeps the schema unambiguous and easy to query with raw SQL.
- At the ORM level, you can use more semantic names for relationships, e.g. author instead of user, owner, or customer. This makes the Python code read more naturally, e.g. post.author.username.

---


#### 5. User registration, login flow, and safe redirects

In the tutorial, after a new user registers, they are redirected to the login page and must log in manually.  
I changed this so that a new user is **automatically logged in immediately after registration**.  

To make the redirect logic safer and more reusable, I also introduced a small helper function get_next_page():


python
def get_next_page(default: str = "index") -> str:
    """
    Returns a safe redirect target from ?next= query parameter.
    Falls back to given default endpoint if next is missing or unsafe.
    """
    next_page = request.args.get("next")
    if not next_page or urlsplit(next_page).netloc != "":
        next_page = url_for(default)
    return next_page


This helper prevents open redirect attacks (by checking netloc) and keeps the code DRY, since both /login and /register reuse it.

Result:

- New users are logged in immediately after registering.

- Both login and registration flows redirect users safely to either their original destination (?next=) or back to /index.

- The user experience is smoother, and the redirect logic is centralized and secure.

---


#### 6. Flask-Login integration

Flask-Login expects user objects to provide certain methods.  
Instead of writing them myself, I use UserMixin, which plugs in sensible defaults:

- is_authenticated – True if the user has valid credentials.  
- is_active – True unless the account is deactivated.  
- is_anonymous – False for real users, True for anonymous visitors.  
- get_id() – Returns the user’s unique ID (as a string).

By inheriting from UserMixin, my User class automatically satisfies Flask-Login’s requirements.

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

---


#### 7. Password hashing experiments (beyond the tutorial)

The tutorial uses Werkzeug’s generate_password_hash() (PBKDF2 by default).  
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

---


#### 8. Forms, validation, and the bridge to Domain-Driven Design

Flask-WTF (and WTForms) provides convenient integration between HTML forms, validation, and Flask routes.  
In this tutorial, forms.py holds classes like LoginForm and RegistrationForm that encapsulate input fields, validation rules, and CSRF protection. This works well for small/medium Flask projects where validation happens close to the web layer.

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

---


#### 9. Implemented an Edit Profile feature

I created a new route /edit_profile protected with @login_required and a corresponding EditProfileForm in forms.py.  
This form allows the user to edit their own profile details such as about_me (and optionally username, if I want to support renaming).  

Key insights:
- Flask-WTF automatically handles validation and CSRF protection, so the form feels native in Flask.
- By pre-populating the form with form = EditProfileForm(obj=current_user) or manually setting fields on GET, I can avoid the "field required" error when opening the page.
- From a design perspective, I realized that allowing username changes is optional and depends on the product: some apps (e.g. Instagram) allow it, others (e.g. GitHub) treat username as immutable.  

---


#### 10. Discovered Jinja sub-templates

Instead of duplicating the HTML for displaying posts in both user.html and index.html, I factored out the repeated markup into _post.html and used {% include "_post.html" %}.  

Key insights:
- This keeps templates DRY (Don’t Repeat Yourself).
- If I later change the post layout, I only need to update _post.html, and the change propagates to all views.  
- Sub-templates are lightweight compared to macros and a perfect fit for repeated UI fragments.

---


#### 11. Experimented with user activity indicators

Using the last_seen field updated via @app.before_request, I displayed “Last seen on …” in the profile page.  
Originally I attempted to use a timeago filter, but Jinja has no such built-in.  

Solutions:
- Use Flask-Moment (tutorial approach) for rich time formatting in the browser.
- Or define my own custom Jinja filter in Python for simple “x minutes ago” strings.
- Or just use strftime() directly to show a formatted datetime.  

Key insight:
Flask’s template layer is minimal by design. Extra formatting often belongs in either:
- A custom filter (Python → Jinja), or
- A JS library (like Moment.js) for better UX.

---


#### 12. Reflections on project structure

By now I’ve seen how each file plays a distinct role in the Flask MVC pattern:
- **routes.py** = Controllers (entry points for HTTP requests).
- **forms.py** = Input validation layer (UI forms, WTForms).
- **models.py** = ORM layer (SQLAlchemy models, persistence logic).
- **templates/** = Views (HTML with Jinja).  

I also added a docstring to each file explaining its purpose and how to think about that part of the app.

This mental model helps me keep responsibilities clear and avoid mixing concerns.  
Long-term, I want to push more business rules into a **domain layer** (dataclasses or Pydantic), keeping Flask as a thin adapter.

---


#### 13. Error handling in Flask

Flask provides an @app.errorhandler(<status_code>) decorator to register custom error pages.
I initially struggled to get my custom 404.html and 500.html templates to render — until I realized that **debug mode overrides them**.

* With FLASK_DEBUG=1, Flask shows its interactive debugger.
* With FLASK_DEBUG=0 (production mode), Flask uses my custom error handlers.

Key insight: Debug mode is for development, not for testing production error handling.

---


#### 14. Email error reporting with aiosmtpd

Instead of sending real emails, I used the aiosmtpd package to spin up a local debugging SMTP server.
This way, error emails are "sent" but just printed to the console. It’s a safe way to test logging without touching a real mail provider.

I extended my .env with mail configuration (server, port, TLS, credentials) and updated config.py to read multiple admin emails from a single environment variable.

---


#### 15. Logging with rotating file handlers

I set up RotatingFileHandler in app/__init__.py to log errors into a logs/ directory.
This keeps log files small, automatically rotates them, and applies a custom formatter for clarity.

Lesson learned: **Good logging is as important as error handling** — it helps detect and debug issues long before users report them.

---


#### 16. Fixing duplicate usernames

While testing /edit_profile, I discovered a **UNIQUE constraint error** when trying to change a username to one that already existed.

Fixes I applied:

* Added db.session.rollback() in my error handler to clean up broken transactions.
* Wrote a custom validate_username() method in EditProfileForm that disallows renaming to an existing username.
* Improved validation to treat John and john as equal (case-insensitive).

To enforce this at the database level, I updated the model:


python
username = orm.mapped_column(sa.String(64, collation="NOCASE"), ...)


The trick was that **collation must be applied at the type level (sa.String)**, not as an argument to Column.

---

#### 17. Database resets in development

My experiments corrupted the database several times. Instead of manually deleting files and migrations, I automated this with a make reset-db target:

1. Remove migrations/, instance/, and app.db.
2. Re-initialize Alembic.
3. Run a fresh migration and upgrade.

This ensures I can always reset to a clean slate in development.
Key insight: For dev work, *resetting is often faster than debugging migration conflicts*.

---


#### 18. Canonical vs Display fields for username and email

The tutorial uses a single `username` and `email` field on the `User` model.
I extended this by introducing **two fields each**:

* `username_canonical` → lowercased, indexed, unique (used for queries & uniqueness checks)

* `username_display` → user’s chosen casing, shown in the UI

* `email_canonical` → lowercased, indexed, unique (used for login & Gravatar)

* `email_display` → original input preserved for display

**Why this matters:**

* Prevents duplicate users differing only by case (`John` vs `john`).
* Keeps DB queries consistent (always lowercase).
* Still respects the user’s preferred formatting in the UI (`NewUSER`, `Name@Domain.com`).

**Insight:**
This pattern mirrors how large systems (like email providers) handle identity: canonical for logic, display for UX.

---

#### 19. Extracting reusable validators into helpers

In the tutorial, each form (e.g. `RegistrationForm`, `EditProfileForm`) had its own duplicated logic for validating usernames and emails.
I refactored this into a **shared helper module**:

`app/helpers/validators.py`

```python
def validate_unique(field, column, original=None, msg="Already taken"):
    ...
```

Usage in forms:

```python
def validate_username(self, username):
    return validate_unique(username, User.username_canonical, msg="Please use a different username.")
```

**Benefits:**

* Centralizes uniqueness logic.
* Easier to maintain: changing rules in one place affects all forms.
* Keeps forms shorter and more focused on their purpose.

**Insight:**
This small refactor is a step toward separating validation concerns from UI, and makes future reuse easier (e.g. for APIs or CLI input).

---


#### 20. Extracted model helpers into reusable modules

In the tutorial, the `User` model directly handled password hashing (`set_password`, `check_password`) and avatar generation (`avatar`).

I refactored this by extracting them into **helper modules**:

* `app/helpers/security.py`

  * `hash_password(password: str) -> str`
  * `verify_password(stored_hash: Optional[str], password: Optional[str]) -> bool`

* `app/helpers/avatar.py`

  * `gravatar_url(email: str, size: int) -> str`

Now the model methods are thin wrappers:

```python
def set_password(self, password: str) -> None:
    self.password_hash = hash_password(password)

def check_password(self, password: Optional[str]) -> bool:
    return verify_password(self.password_hash, password)

def avatar(self, size: int) -> str:
    return gravatar_url(self.email_canonical, size)
```

**Why this matters:**

* Keeps the `User` model focused on persistence (not business logic).
* Easier to test security functions (`hash_password`, `verify_password`) in isolation.
* Future-proof: I can switch from PBKDF2 → Argon2, or Gravatar → custom avatar service, without touching the model.
* By letting `verify_password` handle `None` checks, the model code stays clean and avoids linter warnings about `Optional[str]`.

**Key insight:**
The model exposes a clean API (`user.set_password(...)`, `user.check_password(...)`) but delegates implementation details to helpers. This separation makes the codebase more modular, testable, and maintainable.

---

#### 21. Many-to-many relationships (Core vs ORM)

When implementing the `followers` table (user ↔ user), I noticed Miguel used **SQLAlchemy Core** for the association table instead of ORM.  

**Key insight:**  
- If the association table is a *pure link* (only two FKs, no extra data), it can be defined with **Core** (`sa.Table`).  
- If the association table contains *extra columns* (e.g. timestamp of follow), then it becomes a full model with its own meaning and should be defined with **ORM** (`db.Model`).  

This clarified an important design principle:  
- **Pure association = Core** (lightweight, just linking).  
- **Association + attributes = ORM** (because it has real data beyond the link).  

---

#### 22. Check constraints and idempotency in followers table

I added a **check constraint** to the `followers` association table to prevent a user from following themselves:

```python
sa.CheckConstraint('follower_id != followed_id', name='no_self_follow')
````

I also considered whether I needed an explicit safeguard for **idempotency** (preventing duplicate follows).
After reflection, I realized it’s not necessary:

* The **primary key constraint** on `(follower_id, followed_id)` already ensures uniqueness.
* If I wanted multiple follows (non-idempotent behavior), I would need to add a surrogate primary key (like an auto-increment `id`), but then it would no longer be a pure association table — it would be an entity of its own.

**Key insight:**
Constraints at the database level are simple, powerful, and ensure invariants without extra Python code.

---

#### 23. Using @property for cleaner model APIs

I deviated from the tutorial by making some helper functions into `@property` methods on the `User` model.

Example:

```python
@property
def followers_count(self) -> int:
    ...
```

This allows me to write:

```jinja2
<p>{{ user.followers_count }} followers</p>
```

instead of:

```jinja2
<p>{{ user.followers_count() }} followers</p>
```

**Why it matters:**

* The code reads more cleanly in both Python and Jinja templates.
* `@property` communicates intent: these are **derived attributes**, not actions with side effects.
* It’s especially useful for read-only values like counts or precomputed relationships.

---


#### 24. Password hashing benchmarks and calibration

I wanted to explore password hashing algorithms beyond PBKDF2 (Werkzeug default).

I built **two benchmarking scripts**:

* `benchmarks/run_configs.py` → runs fixed “profiles” (Small device, Balanced, Production, etc.)
* `benchmarks/run_configs.py --calibrate` → dynamically adjusts parameters until hash time ≈ 250ms

**Results on my machine:**

* **PBKDF2** → \~552k iterations for \~280ms.
* **bcrypt** → 13 rounds gave \~410ms.
* **Argon2id** → tunable across three dimensions (`time_cost`, `memory_cost`, `parallelism`).

I tested profiles like *Small device (fast, low memory)*, *Balanced (64MB)*, *Production (128MB)*, *High security (parallelism=3)*, and *Memory-heavy (256MB)*.

**Key insight:**

* Parallelism *reduced runtime* on my CPU while still raising attacker cost.
* Memory-heavy configs are secure but risk DoS if misused.
* The sweet spot on my hardware was **Argon2id (time\_cost=10, memory=128MB, parallelism=3)** at \~320ms.

This confirmed Argon2id is the **modern best-practice choice**, and benchmarking ensures configs match the hardware budget.

---

#### 25. Migrating to Argon2id with pepper

The tutorial uses Werkzeug’s `generate_password_hash` (PBKDF2).
I deviated and switched to **Argon2id**, adding both **salt** (automatic) and **pepper** (from `.env`).

Implementation:

* Added environment variables for **time\_cost, memory\_cost, parallelism, hash\_len, salt\_len, pepper**.
* Built `app/helpers/security.py` with `_get_hasher()` and `_with_pepper()`.
* Updated `User.set_password` and `User.check_password` to delegate to Argon2 helpers.

Because my project is new, I could just **reset the database** and start with Argon2id directly.
In a production system, I’d need to **support legacy hashes** until all users logged in once and were rehashed.

**Key insight:**

* Using pepper raises security significantly (protects even if DB is leaked).
* Centralizing password hashing logic in `helpers/security.py` makes it easier to swap algorithms in the future.
* Environment-driven config gives flexibility: I can tune parameters per environment (dev, staging, production, Raspberry Pi, etc.).

---

#### 26. Email support with Flask-Mail

Today I went through chapter 10: **Email support** and used `flask-mail` to send emails in Flask.

##### `from flask_mail import Mail`

`Mail` is the main Flask-Mail extension class.  
It integrates with the Flask app and manages the SMTP connection.  

Typical setup in `app/__init__.py`:

```python
from flask_mail import Mail
mail = Mail(app)
````

After initialization, use `mail.send(msg)` to send messages.

##### `from flask_mail import Message`

`Message` represents an email message. Attributes:

* `subject: str` → subject line (appears in inbox).
* `sender: str` → email sender (often `app.config['ADMINS'][0]` or `MAIL_DEFAULT_SENDER`).
* `recipients: list[str]` → list of recipients.
* `body: str | None` → plain text body (minimum required).
* `html: str | None` → optional HTML body (recommended).

**Insights:**

* Subject is like a title — keep it short and clear.
* Recipients must always be a list.
* If both `body` and `html` are provided, the email is sent as *multipart/alternative* → client chooses best format.
* HTML can be generated with Jinja templates, e.g.:

```python
msg.body = render_template("email/reset_password.txt", user=user)
msg.html = render_template("email/reset_password.html", user=user)
```

##### Usage example

```python
msg = Message(
    subject="Test subject",
    sender=app.config['ADMINS'][0],
    recipients=["your-email@example.com"],
    body="text body",
    html="<h1>HTML body</h1>",
)
mail.send(msg)
```

**Key insight:**
`Message` is just a container. Actual sending happens via `mail.send(msg)`.
Always include `body`, and include `html` if possible for better UX.

---

#### 27. Alternatives to JWT for reset tokens

The tutorial uses **JWT** for password reset tokens. It works well because:

* Stateless (server stores nothing).
* Securely signed with `SECRET_KEY`.
* Built-in expiration.
* Standardized and debuggable.

But there are alternatives:

**🔹 itsdangerous.URLSafeTimedSerializer**

* Flask-native, supports expiration.
* Simpler, no external deps.
* Not standardized like JWT.

**🔹 Database-stored tokens**

* Random string (UUID or `secrets.token_urlsafe()`), stored with `user_id` + `expires_at`.
* Allows revocation.
* Requires DB lookup each time.

**🔹 Raw UUID/secrets**

* Easiest to generate.
* Needs DB storage to validate.

**Why I chose JWT:**

* No DB overhead.
* Stateless.
* Expiration built-in.
* Widely supported and standardized.

**Key insight:**
JWT isn’t the only way, but it’s a good fit for stateless Flask apps that don’t need revocation logic.

---

#### 28. Debugging issues with email links

When testing reset links with the debug SMTP server, I copied the URL from the terminal output and saw broken links:

```
http://localhost:5000/reset_password/<token></p>\r\n
```

Problem:

* The debug server prints **raw MIME output** (with tags and CRLF).
* Copying directly from the terminal added junk (`</p>` and `\r\n`).

When checking the actual email contents:

```html
<a href="http://localhost:5000/reset_password/<token>">click here</a>
```

…everything was correct.

**Conclusion:**

* Don’t copy links from raw SMTP debug output.
* Use a real mail client, or tools like MailHog/Mailpit.
* The issue wasn’t in Flask or the template — only in how the debug output was copied.

**Key insight:**
Test emails in a real client when links matter. Debug server output can be misleading.

```

---

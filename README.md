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

This is the **first edition** of this README. I will update it as I progress through each tutorial part and deepen my understanding.

---

### Notes:

#### 1.
Use .env + python-dotenv for config loading with make run

Since I'm using `make run` (which executes `python run.py`) instead of `flask run`, I added manual loading of environment variables via `python-dotenv`. This deviates slightly from the tutorial, which assumes `flask run` and automatic `.flaskenv` loading.

Config values like SECRET_KEY are now loaded from a `.env` file in the project root, using `load_dotenv()` in `app/__init__.py`. The `Config` class remains as per the tutorial.

This setup supports the principle of separation of concerns while working well with Makefile-based workflows.

#### 2.

Shell context in app/__init__.py

Instead of creating a separate microblog.py file, I added the @app.shell_context_processor directly in app/__init__.py.

This way, when using flask shell, I get immediate access to:
- db 
- session 
- User 
- Post
- sa
- orm

This reduces boilerplate when exploring the app interactively.

#### 3.
Migration resets in development

While experimenting, I ran into Alembic revision mismatches. In development, the simplest way to recover is to:
```
$ rm x.db  # delete the SQLite database
$ rm -rf migrations/  # delete migration scripts
$ flask db init
$ flask db migrate -m "Initial migration"
$ flask db upgrade
```

#### 4.
This resets both the SQLite database and migrations, which is safe since I’m not preserving production data.

I also learned that ForeignKey is purely SQL (constraints), while relationship and back_populates exist only in the ORM layer to enable OOP-style access (user.posts ↔ post.author). This clarified why both are necessary.

#### 5.
User registration and login flow

In the tutorial, after a new user registers, they are redirected to the login page and must log in manually.  
I changed this so that a new user is **automatically logged in immediately after registration**.  

To support this, I:
- Called `login_user(user)` right after committing the new user in the `/register` route.
- Added a helper function `get_next_page()` to centralize safe handling of the `?next=` query parameter and prevent open redirect attacks.
- Updated both `/login` and `/register` routes to reuse this helper, ensuring users are redirected either to their original destination (if provided) or back to `/index`.

This change improves the user experience by skipping the unnecessary extra login step and keeping the redirect logic DRY and secure.

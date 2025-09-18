# Flask Mega Tutorial Project

This project is based on [Miguel Grinberg's Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and serves as my structured introduction to Flask and full-stack web development.  
Big thanks to Miguel Grinberg for publishing such a detailed and accessible resource.

---

## Purpose

My background so far has been mostly raw coding: writing programs and scripts in `nvim` with minimal dependencies, running them from the terminal, and handling data manually with SQL (MySQL).  

Frameworks, ORMs, templating engines, and deployment were new to me. This project is my way of learning how modern web applications are actually structured.

---

## Learning Objectives

- **Flask** → App factory pattern, routing, request handling.  
- **Jinja2** → Dynamic HTML templating.  
- **HTML/CSS** → Basic frontend structure and styling.  
- **SQLAlchemy ORM** → Mapping Python objects to relational tables.  
- **User auth** → Sessions, login, registration, security.  
- **Error handling & logging** → Graceful error pages, log rotation, email notifications.  
- **Deployment & Docker** → Packaging and running the app outside local dev.  
- **Version control** → Building better Git/GitHub workflow.  

---

## Current Architecture

Over time, I’ve refactored the tutorial into a clearer separation of concerns:

- **Routes (`routes.py`)** → Controllers. Thin entrypoints that map HTTP requests to logic.  
- **Forms (`forms.py`)** → Web layer validation using Flask-WTF.  
- **Domain (`domain.py`)** → Input validation and DTOs (Pydantic models).  
- **Services (`services/`)** → Business logic (e.g. password hashing, avatar generation).  
- **Repositories (`repositories/`)** → Database access (all SQLAlchemy queries).  
- **Models (`models.py`)** → ORM mappings, kept free from domain logic.  
- **Helpers (`helpers/`)** → Navigation and small reusable utilities.  
- **Templates (`templates/`)** → Jinja views with DRY structure (partials like `_post.html`).  

**Mental model:**  
- Routes = CLI entrypoints  
- Forms = Arguments/flags  
- Services = Domain rules / factories  
- Repositories = Database translators  
- Models = Persistence schema  

---

## Project Status

This app is still in development as I go through the tutorial.  

I’m actively extending it with my own experiments:  
- safer redirects  
- domain-driven design principles  
- user profile editing  
- structured logging and error reporting  

---

## How to Run

```bash
make run


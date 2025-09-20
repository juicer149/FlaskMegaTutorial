# Defaults: use system Python if no venv is activated
PYTHON ?= python
PIP ?= pip
FLASK ?= flask

VENV := .venv

# Run the app
run:
	$(FLASK) run

# Flask shell
shell:
	$(FLASK) shell

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Tests
test:
	$(PYTHON) -m unittest discover -v

# Lint with flake8
lint:
	$(PYTHON) -m flake8 app tests.py

# Type checking with mypy
typecheck:
	$(PYTHON) -m mypy app tests.py

# Check formatting with black (does not modify code)
format:
	$(PYTHON) -m black --check app tests.py

# Run all checks
check: lint typecheck format test

# Freeze dependencies (only runtime deps!)
freeze:
	$(PIP) freeze > requirements.txt

# Clean pyc/__pycache__
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +

# Reset DB (dangerous!)
reset-db:
	@read -p "This will do a total reset of the database. Do you wish to continue (y/n) " ans && [ $${ans} = y ]
	rm -rf migrations instance app.db
	$(FLASK) db init
	$(FLASK) db migrate -m "initial migration"
	$(FLASK) db upgrade

.PHONY: run shell freeze install lint format test clean typecheck reset-db check

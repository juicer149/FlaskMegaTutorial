VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
FLASK := $(VENV)/bin/flask

run:
	$(FLASK) run

shell:
	$(FLASK) shell

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -v

lint:
	$(PYTHON) -m flake8 app tests.py

typecheck:
	$(PYTHON) -m mypy app tests.py

format:
	$(PYTHON) -m black app tests.py

check: lint typecheck test

freeze:
	$(PIP) freeze > requirements.txt

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +

reset-db:
	@read -p "This will do a total reset of the database. Do you wish to continue (y/n) " ans && [ $${ans} = y ]
	rm -rf migrations instance app.db
	$(FLASK) db init
	$(FLASK) db migrate -m "initial migration"
	$(FLASK) db upgrade

.PHONY: run shell freeze install lint format test clean typecheck reset-db check

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
FLASK := $(VENV)/bin/flask

run:
	$(FLASK) run

install:
	$(PIP) install -r requirements.txt

freeze:
	pip freeze > requirements.txt


clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +

reset-db:
	@read -p "This will to a total reset of the database. Do you wish to continue (y/n) " ans && [ $${ans} = y ]
	rm -rf migrations instance app.db
	flask db init
	flask db migrate -m "initial migration"
	flask db upgrade


.PHONY: run shell freeze install lint format test clean

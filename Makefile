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


.PHONY: run shell freeze install lint format test clean

.PHONY: install test run

install:
	python3 -m venv .venv
	.venv/bin/pip install -e '.[test]'

test:
	.venv/bin/pytest

run:
	.venv/bin/flask run

run-module:
	.venv/bin/python -m src.main

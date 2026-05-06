.PHONY: install check lint format test

install:
	python -m pip install -e ".[dev]"

check: lint test

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	pytest


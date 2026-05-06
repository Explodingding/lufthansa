.PHONY: install check ingest-raw lint format test

install:
	python -m pip install -e ".[dev]"

check: lint test

ingest-raw:
	airline-ingest-raw --output-dir data/raw

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest


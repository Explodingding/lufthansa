.PHONY: install build-bronze check ingest-raw lint format test

install:
	python -m pip install -e ".[dev]"

check: lint test

build-bronze:
	airline-build-bronze --raw-dir data/raw --output-dir data/bronze

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


$ErrorActionPreference = "Stop"

python -m ruff check .
python -m ruff format --check .
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest


import json
from pathlib import Path

NOTEBOOK_PATH = Path("notebooks/exploratory_analysis.ipynb")


def test_exploratory_notebook_exists() -> None:
    assert NOTEBOOK_PATH.exists()


def test_exploratory_notebook_documents_required_sections() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = _combined_source(notebook)

    required_sections = [
        "Load Available Datasets",
        "Missing Values And Duplicate Checks",
        "Delay Distribution",
        "Business Observations",
        "Candidate Dashboard Metrics",
    ]

    for section in required_sections:
        assert section in source


def test_exploratory_notebook_uses_pandas_and_numpy() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = _combined_source(notebook)

    assert "import pandas as pd" in source
    assert "import numpy as np" in source
    assert "np.percentile" in source


def test_exploratory_notebook_contains_business_observations() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = _combined_source(notebook)

    assert source.count("dashboard") >= 3
    assert "Passenger communication metrics" in source
    assert "Missing enrichment" in source


def _combined_source(notebook: dict) -> str:
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

from pathlib import Path

SQL_DIR = Path("sql")

EXPECTED_SQL_FILES = {
    "route_delay_analysis.sql",
    "airport_disruption_ranking.sql",
    "passenger_communication_impact.sql",
}

GOLD_TABLES = {
    "gold_route_performance",
    "gold_airport_disruption",
    "gold_passenger_communication",
}

FORBIDDEN_LAYER_REFERENCES = (
    "raw_",
    "bronze_",
    "silver_",
    "data/raw",
    "data/bronze",
    "data/silver",
)


def test_sql_insight_files_exist() -> None:
    assert {path.name for path in SQL_DIR.glob("*.sql")} == EXPECTED_SQL_FILES


def test_sql_insights_use_gold_tables_only() -> None:
    for sql_file in SQL_DIR.glob("*.sql"):
        sql = sql_file.read_text(encoding="utf-8").lower()
        assert any(table in sql for table in GOLD_TABLES)
        assert not any(reference in sql for reference in FORBIDDEN_LAYER_REFERENCES)


def test_sql_insights_document_business_questions() -> None:
    for sql_file in SQL_DIR.glob("*.sql"):
        sql = sql_file.read_text(encoding="utf-8")
        assert sql.startswith("-- Question:")
        assert sql.rstrip().endswith(";")

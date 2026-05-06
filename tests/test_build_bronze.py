import pandas as pd
import pytest
from pyspark.sql import SparkSession

from airline_platform.jobs.build_bronze import build_bronze_layer
from airline_platform.jobs.ingest_raw import ingest_synthetic_raw


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.appName("airline-bronze-test")
        .master("local[1]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_build_bronze_layer_writes_parquet_outputs(tmp_path, spark) -> None:
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    ingest_synthetic_raw(raw_dir)

    summary = build_bronze_layer(raw_dir, bronze_dir, spark=spark)

    assert summary.total_records == 9
    assert {source.source for source in summary.sources} == {
        "flights",
        "airports",
        "weather",
        "passenger_events",
    }

    flights = pd.read_parquet(bronze_dir / "flights" / "part-00000.parquet")
    assert len(flights) == 2
    assert "_bronze_loaded_at_utc" in flights.columns
    assert "_source_file" in flights.columns

    assert (bronze_dir / "_build_summary" / "summary.json").exists()


def test_build_bronze_layer_fails_when_raw_source_is_missing(tmp_path, spark) -> None:
    with pytest.raises(FileNotFoundError, match="Missing raw source file"):
        build_bronze_layer(tmp_path / "missing_raw", tmp_path / "bronze", spark=spark)

import pandas as pd
import pytest
from pyspark.sql import SparkSession

from airline_platform.extractors import build_synthetic_data
from airline_platform.jobs.build_bronze import build_bronze_layer
from airline_platform.jobs.build_gold import build_gold_layer
from airline_platform.jobs.build_silver import build_silver_layer
from airline_platform.jobs.ingest_raw import ingest_synthetic_raw


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.appName("airline-gold-test")
        .master("local[1]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_build_gold_layer_writes_business_ready_tables(tmp_path, spark) -> None:
    synthetic_data = build_synthetic_data()
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    gold_dir = tmp_path / "gold"
    ingest_synthetic_raw(raw_dir)
    build_bronze_layer(raw_dir, bronze_dir, spark=spark)
    build_silver_layer(bronze_dir, silver_dir, spark=spark)

    summary = build_gold_layer(silver_dir, gold_dir, spark=spark)

    assert {table.table for table in summary.tables} == {
        "gold_flight_performance",
        "gold_route_performance",
        "gold_airport_disruption",
        "gold_passenger_communication",
    }
    assert summary.total_records > len(synthetic_data.flights)

    flight_performance = pd.read_parquet(gold_dir / "gold_flight_performance")
    assert len(flight_performance) == len(synthetic_data.flights)
    assert {"route", "origin_airport_name", "destination_airport_name"}.issubset(
        flight_performance.columns
    )

    route_performance = pd.read_parquet(gold_dir / "gold_route_performance")
    assert len(route_performance) == 6
    gdn_fra = route_performance.loc[route_performance["route"] == "GDN-FRA"].iloc[0]
    assert gdn_fra["total_flights"] > 100
    assert 0.10 <= gdn_fra["delay_rate"] <= 0.30

    passenger_communication = pd.read_parquet(gold_dir / "gold_passenger_communication")
    assert {
        "delay_notification_sent",
        "mobile_check_in",
        "boarding_pass_viewed",
        "rebooking_offer_viewed",
    }.issubset(set(passenger_communication["event_type"]))

    assert (gold_dir / "_build_summary" / "summary.json").exists()


def test_build_gold_layer_fails_when_silver_source_is_missing(tmp_path, spark) -> None:
    with pytest.raises(FileNotFoundError, match="Missing silver source dataset"):
        build_gold_layer(tmp_path / "missing_silver", tmp_path / "gold", spark=spark)

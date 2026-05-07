import pandas as pd
import pytest
from pyspark.sql import SparkSession

from airline_platform.contracts import SourceContract
from airline_platform.extractors import build_synthetic_data
from airline_platform.jobs.build_bronze import build_bronze_layer
from airline_platform.jobs.build_silver import build_silver_layer
from airline_platform.jobs.ingest_raw import ingest_raw_records, ingest_synthetic_raw


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.appName("airline-silver-test")
        .master("local[1]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_build_silver_layer_writes_cleaned_outputs(tmp_path, spark) -> None:
    synthetic_data = build_synthetic_data()
    expected_total_records = (
        len(synthetic_data.flights)
        + len(synthetic_data.airports)
        + len(synthetic_data.weather)
        + len(synthetic_data.passenger_events)
    )
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    ingest_synthetic_raw(raw_dir)
    build_bronze_layer(raw_dir, bronze_dir, spark=spark)

    summary = build_silver_layer(bronze_dir, silver_dir, spark=spark)

    assert summary.total_records == expected_total_records

    flights = pd.read_parquet(silver_dir / "flights")
    assert len(flights) == len(synthetic_data.flights)
    assert {
        "departure_delay_minutes",
        "is_delayed",
        "is_cancelled",
        "_silver_loaded_at_utc",
    }.issubset(flights.columns)

    delay_rate = flights["is_delayed"].mean()
    cancellation_rate = flights["is_cancelled"].mean()
    assert 0.10 <= delay_rate <= 0.30
    assert 0.0 < cancellation_rate < 0.03

    assert (silver_dir / "_build_summary" / "summary.json").exists()


def test_build_silver_layer_deduplicates_flights_by_flight_id(tmp_path, spark) -> None:
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    source_records = {
        SourceContract.FLIGHTS: [
            {
                "flight_id": "LH-001-2026-05-06",
                "flight_number": "LH001",
                "origin_airport": "GDN",
                "destination_airport": "FRA",
                "scheduled_departure_utc": "2026-05-06T06:30:00Z",
                "actual_departure_utc": "2026-05-06T07:10:00Z",
                "status": "delayed",
            },
            {
                "flight_id": "LH-001-2026-05-06",
                "flight_number": "LH001",
                "origin_airport": "GDN",
                "destination_airport": "FRA",
                "scheduled_departure_utc": "2026-05-06T06:30:00Z",
                "actual_departure_utc": "2026-05-06T07:10:00Z",
                "status": "delayed",
            },
        ],
        SourceContract.AIRPORTS: [
            {
                "airport_code": "GDN",
                "airport_name": "Gdansk Lech Walesa Airport",
                "city": "Gdansk",
                "country": "Poland",
            }
        ],
        SourceContract.WEATHER: [
            {
                "airport_code": "GDN",
                "observed_at_utc": "2026-05-06T06:00:00Z",
                "temperature_c": 12.5,
                "wind_speed_kmh": 22.0,
                "precipitation_mm": 0.2,
            }
        ],
        SourceContract.PASSENGER_EVENTS: [
            {
                "event_id": "evt-001",
                "flight_id": "LH-001-2026-05-06",
                "event_type": "delay_notification_sent",
                "event_timestamp_utc": "2026-05-06T06:36:00Z",
                "channel": "mobile_app",
            }
        ],
    }
    ingest_raw_records(source_records, raw_dir)
    build_bronze_layer(raw_dir, bronze_dir, spark=spark)
    build_silver_layer(bronze_dir, silver_dir, spark=spark)

    flights = pd.read_parquet(silver_dir / "flights")

    assert len(flights) == 1
    assert flights.iloc[0]["departure_delay_minutes"] == 40.0
    assert bool(flights.iloc[0]["is_delayed"]) is True


def test_build_silver_layer_fails_when_bronze_source_is_missing(tmp_path, spark) -> None:
    with pytest.raises(FileNotFoundError, match="Missing bronze source dataset"):
        build_silver_layer(tmp_path / "missing_bronze", tmp_path / "silver", spark=spark)

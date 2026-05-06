import json

import airline_platform.jobs.ingest_raw as ingest_module
from airline_platform.contracts import SourceContract
from airline_platform.extractors import build_synthetic_data
from airline_platform.jobs.ingest_raw import (
    ingest_raw_records,
    ingest_raw_with_airport_source,
    ingest_synthetic_raw,
)


def test_ingest_synthetic_raw_writes_source_files_and_summary(tmp_path) -> None:
    summary = ingest_synthetic_raw(tmp_path)

    assert summary.total_accepted_records == 9
    assert summary.total_rejected_records == 0

    expected_files = {
        "flights.json",
        "airports.json",
        "weather.json",
        "passenger_events.json",
        "validation_summary.json",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected_files

    flights = _read_json(tmp_path / "flights.json")
    assert flights == build_synthetic_data().flights

    validation_summary = _read_json(tmp_path / "validation_summary.json")
    assert validation_summary["output_dir"] == str(tmp_path)
    assert validation_summary["sources"][0] == {
        "source": "flights",
        "accepted_records": 2,
        "rejected_records": 0,
        "errors": [],
    }


def test_ingest_raw_records_rejects_invalid_source_dataset(tmp_path) -> None:
    source_records = {
        SourceContract.FLIGHTS: [
            {
                "flight_id": "",
                "flight_number": "LH001",
                "origin_airport": "GDN",
                "destination_airport": "FRA",
                "scheduled_departure_utc": "2026-05-06T06:30:00Z",
                "status": "boarding",
            }
        ]
    }

    summary = ingest_raw_records(source_records, tmp_path)

    assert summary.total_accepted_records == 0
    assert summary.total_rejected_records == 1

    assert _read_json(tmp_path / "flights.json") == []

    validation_summary = _read_json(tmp_path / "validation_summary.json")
    assert validation_summary["sources"] == [
        {
            "source": "flights",
            "accepted_records": 0,
            "rejected_records": 1,
            "errors": [
                "flights[0] required field is empty: flight_id",
                (
                    "flights[0] invalid value for status: boarding. "
                    "Allowed values: cancelled, delayed, departed, scheduled"
                ),
            ],
        }
    ]


def test_ingest_raw_with_ourairports_replaces_airport_source(tmp_path, monkeypatch) -> None:
    public_airports = [
        {
            "airport_code": "GDN",
            "airport_name": "Gdansk Lech Walesa Airport",
            "city": "Gdansk",
            "country": "PL",
            "latitude_deg": 54.3776,
            "longitude_deg": 18.4662,
        }
    ]
    monkeypatch.setattr(ingest_module, "fetch_ourairports_airports", lambda: public_airports)

    summary = ingest_raw_with_airport_source(tmp_path, airport_source="ourairports")

    assert summary.total_rejected_records == 0
    assert _read_json(tmp_path / "airports.json") == public_airports


def test_ingest_raw_with_ourairports_falls_back_to_synthetic_airports(
    tmp_path,
    monkeypatch,
) -> None:
    def raise_public_source_error():
        raise RuntimeError("public source unavailable")

    monkeypatch.setattr(ingest_module, "fetch_ourairports_airports", raise_public_source_error)

    summary = ingest_raw_with_airport_source(tmp_path, airport_source="ourairports")

    assert summary.total_rejected_records == 0
    assert _read_json(tmp_path / "airports.json") == build_synthetic_data().airports


def test_ingest_raw_with_openmeteo_replaces_weather_source(tmp_path, monkeypatch) -> None:
    public_weather = [
        {
            "airport_code": "GDN",
            "observed_at_utc": "2026-05-06T06:00:00Z",
            "temperature_c": 12.5,
            "wind_speed_kmh": 22.0,
            "precipitation_mm": 0.2,
        }
    ]
    monkeypatch.setattr(
        ingest_module,
        "fetch_openmeteo_weather_for_airports",
        lambda airports, start_date, end_date: public_weather,
    )

    summary = ingest_raw_with_airport_source(
        tmp_path,
        weather_source="openmeteo",
        weather_start_date="2026-05-06",
        weather_end_date="2026-05-06",
    )

    assert summary.total_rejected_records == 0
    assert _read_json(tmp_path / "weather.json") == public_weather


def test_ingest_raw_with_openmeteo_falls_back_to_synthetic_weather(tmp_path, monkeypatch) -> None:
    def raise_public_source_error(airports, start_date, end_date):
        raise RuntimeError("public source unavailable")

    monkeypatch.setattr(
        ingest_module,
        "fetch_openmeteo_weather_for_airports",
        raise_public_source_error,
    )

    summary = ingest_raw_with_airport_source(tmp_path, weather_source="openmeteo")

    assert summary.total_rejected_records == 0
    assert _read_json(tmp_path / "weather.json") == build_synthetic_data().weather


def _read_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)

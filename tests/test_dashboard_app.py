from pathlib import Path

import pandas as pd
import pytest

from dashboard.app import (
    calculate_kpis,
    create_demo_tables,
    filter_tables_by_routes,
    load_dashboard_tables,
    load_gold_tables,
)


def test_calculate_kpis_returns_dashboard_metrics() -> None:
    flight_performance = pd.DataFrame(
        {
            "flight_id": ["LH-001", "LH-002", "LH-003"],
            "is_delayed": [False, True, True],
            "is_cancelled": [False, False, True],
            "departure_delay_minutes": [12.0, 45.0, 0.0],
        }
    )

    kpis = calculate_kpis(flight_performance)

    assert kpis == {
        "total_flights": 3,
        "delayed_flights": 2,
        "cancelled_flights": 1,
        "delay_rate": 2 / 3,
        "average_departure_delay_minutes": 19.0,
    }


def test_filter_tables_by_routes_filters_route_aware_tables() -> None:
    tables = {
        "flight_performance": pd.DataFrame({"route": ["GDN-FRA", "FRA-GDN"]}),
        "route_performance": pd.DataFrame({"route": ["GDN-FRA", "FRA-GDN"]}),
        "airport_disruption": pd.DataFrame({"origin_airport": ["GDN", "FRA"]}),
        "passenger_communication": pd.DataFrame({"route": ["GDN-FRA", "FRA-GDN"]}),
    }

    filtered = filter_tables_by_routes(tables, ["GDN-FRA"])

    assert filtered["flight_performance"]["route"].tolist() == ["GDN-FRA"]
    assert filtered["route_performance"]["route"].tolist() == ["GDN-FRA"]
    assert filtered["passenger_communication"]["route"].tolist() == ["GDN-FRA"]
    assert len(filtered["airport_disruption"]) == 2


def test_load_gold_tables_reads_required_parquet_tables(tmp_path) -> None:
    _write_parquet_table(
        tmp_path,
        "gold_flight_performance",
        pd.DataFrame(
            {
                "flight_id": ["LH-001"],
                "route": ["GDN-FRA"],
                "is_delayed": [False],
                "is_cancelled": [False],
                "departure_delay_minutes": [12.0],
            }
        ),
    )
    _write_parquet_table(
        tmp_path,
        "gold_route_performance",
        pd.DataFrame({"route": ["GDN-FRA"], "total_flights": [1]}),
    )
    _write_parquet_table(
        tmp_path,
        "gold_airport_disruption",
        pd.DataFrame({"origin_airport": ["GDN"], "total_departures": [1]}),
    )
    _write_parquet_table(
        tmp_path,
        "gold_passenger_communication",
        pd.DataFrame({"route": ["GDN-FRA"], "event_count": [1]}),
    )

    tables = load_gold_tables(tmp_path)

    assert set(tables) == {
        "flight_performance",
        "route_performance",
        "airport_disruption",
        "passenger_communication",
    }
    assert tables["flight_performance"].iloc[0]["route"] == "GDN-FRA"


def test_load_gold_tables_fails_when_required_table_is_missing(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="Missing gold table"):
        load_gold_tables(tmp_path)


def test_load_dashboard_tables_uses_demo_data_when_gold_tables_are_missing(tmp_path) -> None:
    tables, using_demo_data = load_dashboard_tables(tmp_path)

    assert using_demo_data is True
    assert set(tables) == {
        "flight_performance",
        "route_performance",
        "airport_disruption",
        "passenger_communication",
    }
    assert len(tables["flight_performance"]) > 0


def test_create_demo_tables_supports_dashboard_kpis() -> None:
    tables = create_demo_tables()
    kpis = calculate_kpis(tables["flight_performance"])

    assert kpis["total_flights"] == 3
    assert kpis["delayed_flights"] == 2
    assert kpis["cancelled_flights"] == 1


def _write_parquet_table(base_dir: Path, table_name: str, frame: pd.DataFrame) -> None:
    table_dir = base_dir / table_name
    table_dir.mkdir(parents=True)
    frame.to_parquet(table_dir / "part-00000.parquet", index=False)

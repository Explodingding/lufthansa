from pathlib import Path

import pandas as pd
import pytest

from dashboard.app import (
    build_delay_risk_heatmap,
    build_weather_delay_view,
    calculate_kpis,
    calculate_weather_delay_summary,
    create_demo_tables,
    filter_flight_performance,
    filter_route_performance,
    filter_tables_by_routes,
    load_dashboard_tables,
    load_gold_tables,
    sort_and_limit_routes,
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


def test_filter_flight_performance_applies_disruption_and_weather_filters() -> None:
    tables = create_demo_tables()

    filtered = filter_flight_performance(
        tables["flight_performance"],
        delayed_only=True,
        wind_speed_range=(25.0, 45.0),
    )

    assert not filtered.empty
    assert filtered["is_delayed"].all()
    assert filtered["origin_wind_speed_kmh"].between(25.0, 45.0).all()


def test_filter_route_performance_applies_minimum_delay_rate() -> None:
    tables = create_demo_tables()

    filtered = filter_route_performance(tables["route_performance"], minimum_delay_rate=0.2)

    assert not filtered.empty
    assert (filtered["delay_rate"] >= 0.2).all()


def test_sort_and_limit_routes_returns_requested_top_n() -> None:
    tables = create_demo_tables()

    top_routes = sort_and_limit_routes(
        tables["route_performance"],
        sort_by="Delay rate",
        top_n=3,
    )

    assert len(top_routes) == 3
    assert top_routes["delay_rate"].is_monotonic_decreasing


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

    assert kpis["total_flights"] == 720
    assert 0.10 <= kpis["delay_rate"] <= 0.30
    assert 0 < kpis["cancelled_flights"] < 25
    assert "origin_wind_speed_kmh" in tables["flight_performance"].columns


def test_calculate_weather_delay_summary_returns_correlation() -> None:
    tables = create_demo_tables()

    summary = calculate_weather_delay_summary(tables["flight_performance"])

    assert summary["average_wind_speed_kmh"] is not None
    assert summary["wind_delay_correlation"] is not None
    assert summary["wind_delay_correlation"] > 0


def test_build_weather_delay_view_groups_flights_by_wind_bucket() -> None:
    tables = create_demo_tables()

    weather_delay_view = build_weather_delay_view(tables["flight_performance"])

    assert set(weather_delay_view["wind_bucket"].astype(str)).issubset(
        {"0-15 km/h", "15-25 km/h", "25-35 km/h", "35+ km/h"}
    )
    assert weather_delay_view["total_flights"].sum() == 720


def test_build_delay_risk_heatmap_returns_route_wind_probability_matrix() -> None:
    tables = create_demo_tables()

    heatmap = build_delay_risk_heatmap(
        tables["flight_performance"],
        minimum_segment_flights=5,
    )

    assert not heatmap.empty
    assert set(heatmap.index).issubset(set(tables["route_performance"]["route"]))
    assert heatmap.columns.astype(str).tolist() == [
        "0-15 km/h",
        "15-25 km/h",
        "25-35 km/h",
        "35+ km/h",
    ]
    assert heatmap.min(skipna=True).min() >= 0
    assert heatmap.max(skipna=True).max() <= 1


def test_build_delay_risk_heatmap_respects_minimum_segment_size() -> None:
    tables = create_demo_tables()

    heatmap = build_delay_risk_heatmap(
        tables["flight_performance"],
        minimum_segment_flights=1_000,
    )

    assert heatmap.empty


def _write_parquet_table(base_dir: Path, table_name: str, frame: pd.DataFrame) -> None:
    table_dir = base_dir / table_name
    table_dir.mkdir(parents=True)
    frame.to_parquet(table_dir / "part-00000.parquet", index=False)

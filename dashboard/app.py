"""Streamlit dashboard for gold-layer airline disruption metrics."""

from pathlib import Path

import pandas as pd
import streamlit as st

GOLD_DIR = Path("data/gold")
REQUIRED_GOLD_TABLES = {
    "flight_performance": "gold_flight_performance",
    "route_performance": "gold_route_performance",
    "airport_disruption": "gold_airport_disruption",
    "passenger_communication": "gold_passenger_communication",
}


def load_gold_tables(gold_dir: Path = GOLD_DIR) -> dict[str, pd.DataFrame]:
    """Load dashboard-ready gold tables from a local Parquet data lake folder."""

    tables: dict[str, pd.DataFrame] = {}
    for logical_name, table_name in REQUIRED_GOLD_TABLES.items():
        table_path = gold_dir / table_name
        if not table_path.exists():
            message = (
                f"Missing gold table: {table_path}. "
                "Run airline-build-gold --silver-dir data/silver --output-dir data/gold first."
            )
            raise FileNotFoundError(message)
        tables[logical_name] = pd.read_parquet(table_path)

    return tables


def load_dashboard_tables(gold_dir: Path = GOLD_DIR) -> tuple[dict[str, pd.DataFrame], bool]:
    """Load gold tables or return embedded demo data for hosted review environments."""

    try:
        return load_gold_tables(gold_dir), False
    except FileNotFoundError:
        return create_demo_tables(), True


def create_demo_tables() -> dict[str, pd.DataFrame]:
    """Create a small dashboard-ready dataset for Streamlit Community Cloud."""

    flight_performance = _create_demo_flight_performance()
    route_performance = _create_demo_route_performance(flight_performance)
    airport_disruption = _create_demo_airport_disruption(flight_performance)
    passenger_communication = _create_demo_passenger_communication(flight_performance)

    return {
        "flight_performance": flight_performance,
        "route_performance": route_performance,
        "airport_disruption": airport_disruption,
        "passenger_communication": passenger_communication,
    }


def _create_demo_flight_performance(flight_count: int = 720) -> pd.DataFrame:
    routes = (
        ("GDN", "FRA"),
        ("FRA", "GDN"),
        ("GDN", "MUC"),
        ("MUC", "GDN"),
        ("WAW", "FRA"),
        ("ZRH", "MUC"),
    )
    rows: list[dict[str, object]] = []
    for index in range(flight_count):
        origin_airport, destination_airport = routes[index % len(routes)]
        route = f"{origin_airport}-{destination_airport}"
        is_cancelled = index % 97 == 0
        is_delayed = not is_cancelled and index % 10 in {0, 1}
        wind_speed = _demo_wind_speed_for(index, is_delayed)
        precipitation = round(((index * 5) % 11) * 0.25, 2)
        delay_minutes = (
            float(16 + (index * 5) % 45 + max(wind_speed - 24, 0) * 0.8)
            if is_delayed
            else float(index % 13)
        )
        if is_cancelled:
            delay_minutes = 0.0

        rows.append(
            {
                "flight_id": f"LH{1000 + index}-2026-05-{1 + index % 30:02d}",
                "route": route,
                "origin_airport": origin_airport,
                "destination_airport": destination_airport,
                "is_delayed": is_delayed,
                "is_cancelled": is_cancelled,
                "departure_delay_minutes": delay_minutes,
                "origin_temperature_c": round(8.0 + (index % 16) * 0.9, 1),
                "origin_wind_speed_kmh": wind_speed,
                "origin_precipitation_mm": precipitation,
            }
        )

    return pd.DataFrame(rows)


def _create_demo_route_performance(flight_performance: pd.DataFrame) -> pd.DataFrame:
    route_performance = (
        flight_performance.groupby("route", as_index=False)
        .agg(
            total_flights=("flight_id", "count"),
            delayed_flights=("is_delayed", "sum"),
            cancelled_flights=("is_cancelled", "sum"),
            average_departure_delay_minutes=("departure_delay_minutes", "mean"),
        )
        .sort_values("route")
    )
    route_performance["delay_rate"] = (
        route_performance["delayed_flights"] / route_performance["total_flights"]
    )
    return route_performance


def _create_demo_airport_disruption(flight_performance: pd.DataFrame) -> pd.DataFrame:
    airport_metadata = pd.DataFrame(
        {
            "origin_airport": ["GDN", "FRA", "MUC", "WAW", "ZRH"],
            "airport_name": [
                "Gdansk Lech Walesa Airport",
                "Frankfurt Airport",
                "Munich Airport",
                "Warsaw Chopin Airport",
                "Zurich Airport",
            ],
            "city": ["Gdansk", "Frankfurt", "Munich", "Warsaw", "Zurich"],
            "country": ["Poland", "Germany", "Germany", "Poland", "Switzerland"],
        }
    )
    airport_disruption = (
        flight_performance.groupby("origin_airport", as_index=False)
        .agg(
            total_departures=("flight_id", "count"),
            delayed_departures=("is_delayed", "sum"),
            cancelled_departures=("is_cancelled", "sum"),
            average_departure_delay_minutes=("departure_delay_minutes", "mean"),
        )
        .merge(airport_metadata, on="origin_airport", how="left")
    )
    airport_disruption["delay_rate"] = (
        airport_disruption["delayed_departures"] / airport_disruption["total_departures"]
    )
    return airport_disruption


def _create_demo_passenger_communication(flight_performance: pd.DataFrame) -> pd.DataFrame:
    event_rows: list[dict[str, object]] = []
    for index, flight in flight_performance.iterrows():
        if index % 4 == 0:
            event_rows.append(
                {
                    "route": flight["route"],
                    "event_type": "mobile_check_in",
                    "channel": "mobile_app",
                    "is_delayed": flight["is_delayed"],
                    "is_cancelled": flight["is_cancelled"],
                }
            )
        if bool(flight["is_delayed"]):
            event_rows.append(
                {
                    "route": flight["route"],
                    "event_type": "delay_notification_sent",
                    "channel": "mobile_app",
                    "is_delayed": True,
                    "is_cancelled": False,
                }
            )
        if bool(flight["is_cancelled"]):
            event_rows.append(
                {
                    "route": flight["route"],
                    "event_type": "rebooking_offer_viewed",
                    "channel": "email",
                    "is_delayed": False,
                    "is_cancelled": True,
                }
            )

    events = pd.DataFrame(event_rows)
    return (
        events.groupby(["route", "event_type", "channel"], as_index=False)
        .agg(
            event_count=("route", "count"),
            delayed_flight_events=("is_delayed", "sum"),
            cancelled_flight_events=("is_cancelled", "sum"),
        )
        .sort_values(["route", "event_type", "channel"])
    )


def _demo_wind_speed_for(index: int, is_delayed: bool) -> float:
    baseline_wind = 8 + (index * 7) % 34
    disruption_wind_lift = 4 + index % 6 if is_delayed else 0
    return float(baseline_wind + disruption_wind_lift)


def calculate_kpis(flight_performance: pd.DataFrame) -> dict[str, float]:
    """Calculate high-level dashboard KPIs from flight-level gold data."""

    total_flights = len(flight_performance)
    delayed_flights = int(flight_performance["is_delayed"].sum()) if total_flights else 0
    cancelled_flights = int(flight_performance["is_cancelled"].sum()) if total_flights else 0
    average_delay = (
        float(flight_performance["departure_delay_minutes"].mean()) if total_flights else 0.0
    )
    delay_rate = delayed_flights / total_flights if total_flights else 0.0

    return {
        "total_flights": total_flights,
        "delayed_flights": delayed_flights,
        "cancelled_flights": cancelled_flights,
        "delay_rate": delay_rate,
        "average_departure_delay_minutes": average_delay,
    }


def calculate_weather_delay_summary(flight_performance: pd.DataFrame) -> dict[str, float | None]:
    """Calculate weather-delay relationship metrics for dashboard interpretation."""

    required_columns = {"origin_wind_speed_kmh", "departure_delay_minutes"}
    if not required_columns.issubset(flight_performance.columns) or len(flight_performance) < 2:
        return {
            "average_wind_speed_kmh": None,
            "wind_delay_correlation": None,
        }

    weather_delay = flight_performance[
        ["origin_wind_speed_kmh", "departure_delay_minutes"]
    ].dropna()
    if len(weather_delay) < 2:
        return {
            "average_wind_speed_kmh": None,
            "wind_delay_correlation": None,
        }

    return {
        "average_wind_speed_kmh": float(weather_delay["origin_wind_speed_kmh"].mean()),
        "wind_delay_correlation": float(
            weather_delay["origin_wind_speed_kmh"].corr(weather_delay["departure_delay_minutes"])
        ),
    }


def build_weather_delay_view(flight_performance: pd.DataFrame) -> pd.DataFrame:
    """Group delay metrics by wind-speed bucket."""

    required_columns = {
        "origin_wind_speed_kmh",
        "departure_delay_minutes",
        "is_delayed",
        "flight_id",
    }
    if not required_columns.issubset(flight_performance.columns):
        return pd.DataFrame()

    weather_delay = flight_performance[
        [
            "flight_id",
            "origin_wind_speed_kmh",
            "departure_delay_minutes",
            "is_delayed",
        ]
    ].dropna()
    if weather_delay.empty:
        return pd.DataFrame()

    weather_delay = weather_delay.copy()
    weather_delay["wind_bucket"] = pd.cut(
        weather_delay["origin_wind_speed_kmh"],
        bins=[0, 15, 25, 35, 100],
        labels=["0-15 km/h", "15-25 km/h", "25-35 km/h", "35+ km/h"],
        include_lowest=True,
    )

    view = (
        weather_delay.groupby("wind_bucket", observed=True)
        .agg(
            total_flights=("flight_id", "count"),
            delayed_flights=("is_delayed", "sum"),
            average_departure_delay_minutes=("departure_delay_minutes", "mean"),
            average_wind_speed_kmh=("origin_wind_speed_kmh", "mean"),
        )
        .reset_index()
    )
    view["delay_rate"] = view["delayed_flights"] / view["total_flights"]
    return view


def filter_tables_by_routes(
    tables: dict[str, pd.DataFrame],
    selected_routes: list[str],
) -> dict[str, pd.DataFrame]:
    """Filter route-aware gold tables by selected routes."""

    if not selected_routes:
        return tables

    filtered = tables.copy()
    for table_name in ("flight_performance", "route_performance", "passenger_communication"):
        table = filtered[table_name]
        if "route" in table.columns:
            filtered[table_name] = table.loc[table["route"].isin(selected_routes)].copy()

    return filtered


def _format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


@st.cache_data(show_spinner=False)
def _cached_load_dashboard_tables(gold_dir: str) -> tuple[dict[str, pd.DataFrame], bool]:
    return load_dashboard_tables(Path(gold_dir))


def main() -> None:
    """Render the Streamlit dashboard."""

    st.set_page_config(
        page_title="Airline Digital Experience Dashboard",
        layout="wide",
    )
    st.title("Airline Digital Experience Dashboard")
    st.caption(
        "Gold-layer view of flight disruption, route performance, airport impact, "
        "and passenger communication."
    )

    gold_dir = st.sidebar.text_input("Gold data directory", value=str(GOLD_DIR))

    tables, using_demo_data = _cached_load_dashboard_tables(gold_dir)
    if using_demo_data:
        st.info(
            "Using embedded demo data because local gold Parquet tables were not found. "
            "Run the pipeline locally to use data/gold outputs."
        )

    route_options = sorted(tables["route_performance"]["route"].dropna().unique().tolist())
    selected_routes = st.sidebar.multiselect(
        "Routes",
        options=route_options,
        default=route_options,
        help="Filter route-aware dashboard views.",
    )
    filtered_tables = filter_tables_by_routes(tables, selected_routes)
    kpis = calculate_kpis(filtered_tables["flight_performance"])
    weather_summary = calculate_weather_delay_summary(filtered_tables["flight_performance"])

    st.subheader("Operational KPIs")
    metric_columns = st.columns(5)
    metric_columns[0].metric("Total flights", f"{kpis['total_flights']:,}")
    metric_columns[1].metric("Delayed flights", f"{kpis['delayed_flights']:,}")
    metric_columns[2].metric("Cancelled flights", f"{kpis['cancelled_flights']:,}")
    metric_columns[3].metric("Delay rate", _format_percentage(kpis["delay_rate"]))
    metric_columns[4].metric(
        "Avg departure delay",
        f"{kpis['average_departure_delay_minutes']:.1f} min",
    )

    st.subheader("Route Performance")
    route_view = filtered_tables["route_performance"].sort_values(
        ["delay_rate", "average_departure_delay_minutes"],
        ascending=[False, False],
    )
    st.dataframe(
        route_view[
            [
                "route",
                "total_flights",
                "delayed_flights",
                "cancelled_flights",
                "delay_rate",
                "average_departure_delay_minutes",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Weather vs Departure Delay")
    weather_metric_columns = st.columns(2)
    average_wind = weather_summary["average_wind_speed_kmh"]
    wind_correlation = weather_summary["wind_delay_correlation"]
    weather_metric_columns[0].metric(
        "Avg origin wind speed",
        "n/a" if average_wind is None else f"{average_wind:.1f} km/h",
    )
    weather_metric_columns[1].metric(
        "Wind-delay correlation",
        "n/a" if wind_correlation is None else f"{wind_correlation:.2f}",
        help="Pearson correlation between origin wind speed and departure delay minutes.",
    )
    weather_delay_view = build_weather_delay_view(filtered_tables["flight_performance"])
    if weather_delay_view.empty:
        st.info("Weather enrichment fields are not available for the selected data.")
    else:
        st.dataframe(
            weather_delay_view[
                [
                    "wind_bucket",
                    "total_flights",
                    "delayed_flights",
                    "delay_rate",
                    "average_departure_delay_minutes",
                    "average_wind_speed_kmh",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Airport Disruption")
    airport_view = filtered_tables["airport_disruption"].sort_values(
        ["delay_rate", "cancelled_departures", "average_departure_delay_minutes"],
        ascending=[False, False, False],
    )
    st.dataframe(
        airport_view[
            [
                "origin_airport",
                "airport_name",
                "city",
                "country",
                "total_departures",
                "delayed_departures",
                "cancelled_departures",
                "delay_rate",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Passenger Communication Around Disruptions")
    communication_view = filtered_tables["passenger_communication"].sort_values(
        ["delayed_flight_events", "cancelled_flight_events", "event_count"],
        ascending=[False, False, False],
    )
    st.dataframe(
        communication_view[
            [
                "route",
                "event_type",
                "channel",
                "event_count",
                "delayed_flight_events",
                "cancelled_flight_events",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Metric definitions"):
        st.markdown(
            """
            - **Delayed flight**: `departure_delay_minutes > 15`.
            - **Cancelled flight**: flight status equals `cancelled`.
            - **Delay rate**: delayed flights divided by total flights.
            - **Average departure delay**: mean of `departure_delay_minutes` in the selected view.
            - **Wind-delay correlation**: Pearson correlation between origin wind speed and
              departure delay minutes. It is exploratory, not a causal model.
            - **Passenger communication events**: grouped Digital Hangar-style communication events
              connected to flight disruption context.
            """
        )


if __name__ == "__main__":
    main()

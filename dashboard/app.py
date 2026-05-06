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
def _cached_load_gold_tables(gold_dir: str) -> dict[str, pd.DataFrame]:
    return load_gold_tables(Path(gold_dir))


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

    try:
        tables = _cached_load_gold_tables(gold_dir)
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    route_options = sorted(tables["route_performance"]["route"].dropna().unique().tolist())
    selected_routes = st.sidebar.multiselect(
        "Routes",
        options=route_options,
        default=route_options,
        help="Filter route-aware dashboard views.",
    )
    filtered_tables = filter_tables_by_routes(tables, selected_routes)
    kpis = calculate_kpis(filtered_tables["flight_performance"])

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
            - **Passenger communication events**: grouped Digital Hangar-style communication events
              connected to flight disruption context.
            """
        )


if __name__ == "__main__":
    main()

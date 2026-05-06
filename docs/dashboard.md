# Streamlit Dashboard

The Streamlit dashboard provides a recruiter-friendly product view over the gold layer.

## Purpose

The dashboard is designed for a Digital Hangar-style product conversation. It shows how flight disruption metrics can be connected to route performance, airport impact, and passenger communication events.

## Input Data

The dashboard reads local gold Parquet tables:

- `data/gold/gold_flight_performance/`
- `data/gold/gold_route_performance/`
- `data/gold/gold_airport_disruption/`
- `data/gold/gold_passenger_communication/`

Before running the dashboard, build the pipeline:

```powershell
airline-ingest-raw --output-dir data/raw
airline-build-bronze --raw-dir data/raw --output-dir data/bronze
airline-build-silver --bronze-dir data/bronze --output-dir data/silver
airline-build-gold --silver-dir data/silver --output-dir data/gold
```

## Run Locally

```powershell
streamlit run dashboard/app.py
```

## Dashboard Views

The dashboard includes:

- operational KPIs: total flights, delayed flights, cancelled flights, delay rate, and average departure delay,
- route performance table,
- airport disruption table,
- passenger communication table,
- route filter,
- metric definitions.

## Metric Definitions

- **Delayed flight**: `departure_delay_minutes > 15`.
- **Cancelled flight**: flight status equals `cancelled`.
- **Delay rate**: delayed flights divided by total flights.
- **Average departure delay**: mean of `departure_delay_minutes` in the selected view.
- **Passenger communication events**: communication records connected to flight disruption context.


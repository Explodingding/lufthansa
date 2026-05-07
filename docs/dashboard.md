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

If these local files are not available, for example in Streamlit Community Cloud, the dashboard falls back to an embedded demo dataset with 720 representative flights across six routes. This keeps the hosted app reviewable while preserving the local gold-layer workflow for full pipeline demos.

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

## Streamlit Community Cloud

Recommended deployment settings:

- repository: `Explodingding/lufthansa`,
- branch: `cursor/day-1-foundation` until the work is merged to `master`,
- main file path: `dashboard/app.py`.

The app uses `requirements.txt` for a lightweight hosted dashboard environment. The full local project remains configured in `pyproject.toml`.

## Dashboard Views

The dashboard includes:

- operational KPIs: total flights, delayed flights, cancelled flights, delay rate, and average departure delay,
- route performance table,
- airport disruption table,
- weather vs departure delay exploration,
- delay risk heatmap by route and wind-speed bucket,
- passenger communication table,
- route, delay, cancellation, and wind-speed filters,
- route sorting and top-N display controls,
- metric definitions.

## Metric Definitions

- **Delayed flight**: `departure_delay_minutes > 15`.
- **Cancelled flight**: flight status equals `cancelled`.
- **Delay rate**: delayed flights divided by total flights.
- **Delay risk heatmap**: observed delay probability for route and wind-speed combinations. It helps identify statistical signals for investigation, but it is not a causal model.
- **Average departure delay**: mean of `departure_delay_minutes` in the selected view.
- **Wind-delay correlation**: Pearson correlation between origin wind speed and departure delay minutes. This is an exploratory indicator, not a causal model.
- **Passenger communication events**: communication records connected to flight disruption context.


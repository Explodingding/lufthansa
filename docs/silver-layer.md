# Silver Layer

The silver layer turns source-aligned bronze datasets into cleaned datasets that are ready for joins, analysis, and later gold-level business modeling.

## Purpose

Silver should:

- read bronze Parquet datasets,
- deduplicate records by business keys,
- standardize controlled values,
- calculate basic derived fields,
- keep datasets join-ready,
- write cleaned Parquet outputs.

## Inputs

Expected bronze datasets:

- `data/bronze/flights/`
- `data/bronze/airports/`
- `data/bronze/weather/`
- `data/bronze/passenger_events/`

These datasets are created by:

```bash
airline-build-bronze --raw-dir data/raw --output-dir data/bronze
```

## Outputs

Expected silver outputs:

- `data/silver/flights/`
- `data/silver/airports/`
- `data/silver/weather/`
- `data/silver/passenger_events/`
- `data/silver/_build_summary/`

## Flight Cleaning Rules

The silver flights dataset adds:

- `departure_delay_minutes`,
- `is_delayed`,
- `is_cancelled`,
- `_silver_loaded_at_utc`.

Business rules:

- `departure_delay_minutes` is calculated from actual vs scheduled departure.
- Negative delays are floored at `0`.
- `is_delayed` is true when delay is greater than 15 minutes.
- `is_cancelled` is derived from the normalized flight status.

## Join Readiness

The silver layer keeps keys that will be needed later:

- flights keep `origin_airport` and `destination_airport`,
- airports keep `airport_code`,
- weather keeps `airport_code` and `observed_at_utc`,
- passenger events keep `flight_id`.

Gold-layer jobs will use these fields for route, airport, weather, and passenger communication metrics.


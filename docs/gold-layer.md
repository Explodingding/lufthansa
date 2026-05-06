# Gold Layer

The gold layer turns cleaned silver datasets into business-ready tables for SQL insights and the Streamlit dashboard.

## Purpose

Gold should:

- read cleaned silver datasets,
- join flight data with airport, weather, and passenger-event context,
- calculate route and airport performance metrics,
- provide stable tables for SQL and dashboarding,
- keep metric definitions transparent.

## Inputs

Expected silver datasets:

- `data/silver/flights/`
- `data/silver/airports/`
- `data/silver/weather/`
- `data/silver/passenger_events/`

These datasets are created by:

```bash
airline-build-silver --bronze-dir data/bronze --output-dir data/silver
```

## Outputs

Expected gold tables:

- `data/gold/gold_flight_performance/`
- `data/gold/gold_route_performance/`
- `data/gold/gold_airport_disruption/`
- `data/gold/gold_passenger_communication/`
- `data/gold/_build_summary/`

## Gold Tables

### `gold_flight_performance`

One row per flight enriched with route, airport, weather, delay, and cancellation context.

Primary use:

- detailed flight-level dashboard table,
- source for route and airport aggregates,
- debugging metric calculations.

### `gold_route_performance`

One row per route.

Metrics:

- `total_flights`,
- `delayed_flights`,
- `cancelled_flights`,
- `average_departure_delay_minutes`,
- `delay_rate`.

### `gold_airport_disruption`

One row per origin airport.

Metrics:

- `total_departures`,
- `delayed_departures`,
- `cancelled_departures`,
- `average_departure_delay_minutes`,
- `delay_rate`.

### `gold_passenger_communication`

Passenger event metrics grouped by event type, channel, and route.

Metrics:

- `event_count`,
- `delayed_flight_events`,
- `cancelled_flight_events`.

## Dashboard Readiness

These tables are designed to answer the first Digital Hangar dashboard questions:

- Which routes have the highest delay rate?
- Which airports contribute most to disruption impact?
- Which passenger communication events happen around disruptions?
- What is the overall delay and cancellation picture?


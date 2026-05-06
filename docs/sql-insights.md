# SQL Insights

The SQL layer demonstrates how a business analyst or product owner could inspect gold-layer metrics without reading Python pipeline code.

## Purpose

The queries are intentionally written against gold tables only. This keeps the analysis close to the dashboard-ready data model and avoids duplicating transformation logic from raw, bronze, or silver layers.

## Queries

### `sql/route_delay_analysis.sql`

Business question:

Which routes have the highest delay impact and should be reviewed first?

Expected interpretation:

- routes with higher `delay_rate_pct` and average departure delay are stronger candidates for operational review,
- cancelled flights are shown beside delays because they also affect passenger experience,
- this query is a direct input for a "top disrupted routes" dashboard component.

### `sql/airport_disruption_ranking.sql`

Business question:

Which origin airports contribute most to departure disruption?

Expected interpretation:

- airports with high delay rates or cancellation counts can be investigated for operational bottlenecks,
- city and country fields make the output understandable outside the engineering team,
- this query supports an airport-level disruption table or map.

### `sql/passenger_communication_impact.sql`

Business question:

Which passenger communication channels are most active around disrupted flights?

Expected interpretation:

- high event counts around delayed or cancelled flights show where passengers receive disruption-related communication,
- grouping by channel helps compare mobile app, email, and other communication surfaces,
- this query connects flight operations to Digital Hangar's passenger-facing product experience.

## Execution Context

These queries are meant to be portable examples for:

- Databricks SQL over registered gold tables,
- a local analytical database after loading `data/gold/*` Parquet datasets,
- a reviewer reading the repository to understand the business questions behind the dashboard.


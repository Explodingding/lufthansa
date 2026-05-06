# Exploratory Analysis

The exploratory analysis notebook documents the first data-understanding pass before dashboard design.

Notebook:

- `notebooks/exploratory_analysis.ipynb`

## Purpose

The notebook demonstrates:

- loading silver and gold Parquet datasets with Pandas,
- basic dataset inventory,
- missing value checks,
- duplicate checks,
- delay distribution analysis with NumPy,
- business observations that influence dashboard metric selection.

## Main Observations

1. Route-level delay rate is a better first dashboard ranking metric than raw delayed-flight count because it normalizes by the number of flights.
2. Airport disruption should remain a separate dashboard view because origin airports can explain operational bottlenecks that route-only aggregates hide.
3. Passenger communication metrics connect operational disruption with Digital Hangar product surfaces, making the analysis relevant beyond pure flight operations.
4. Missing enrichment should stay visible because public API data can be incomplete or unavailable in local/demo runs.

## Candidate Metrics Confirmed By EDA

- total flights,
- delayed flights,
- cancelled flights,
- delay rate,
- average departure delay,
- top disrupted routes,
- airport disruption ranking,
- passenger communication events around disruptions.

## Run Context

Build the data lake before opening the notebook:

```powershell
airline-ingest-raw --output-dir data/raw
airline-build-bronze --raw-dir data/raw --output-dir data/bronze
airline-build-silver --bronze-dir data/bronze --output-dir data/silver
airline-build-gold --silver-dir data/silver --output-dir data/gold
```


# Bronze Layer

The bronze layer is the first structured data lake layer after raw ingestion.

## Purpose

Bronze keeps the data close to the source shape while making it easier to process with Spark.

It should:

- read validated raw JSON files,
- apply explicit schemas derived from source contracts,
- keep source-aligned fields,
- add minimal technical metadata,
- write Spark-readable Parquet outputs.

## Inputs

Expected raw files:

- `data/raw/flights.json`
- `data/raw/airports.json`
- `data/raw/weather.json`
- `data/raw/passenger_events.json`

These files are created by:

```bash
airline-ingest-raw --output-dir data/raw
```

## Outputs

Expected bronze outputs:

- `data/bronze/flights/`
- `data/bronze/airports/`
- `data/bronze/weather/`
- `data/bronze/passenger_events/`
- `data/bronze/_build_summary/`

The build summary stores source-level record counts for review and debugging.

On Windows machines without `HADOOP_HOME`, the local implementation writes Parquet through Pandas/PyArrow after Spark has read and structured the data. On Databricks or Linux-like Spark environments, native Spark Parquet writing can be used.

## Technical Metadata

Each bronze dataset includes:

- `_bronze_loaded_at_utc`: timestamp when the record entered bronze,
- `_source_file`: raw source file path used by Spark.

## What Bronze Does Not Do

Bronze does not apply business cleaning yet.

It should not:

- deduplicate business records,
- calculate delay metrics,
- join flights with airports or weather,
- create dashboard-ready tables.

Those responsibilities belong to the silver and gold layers.


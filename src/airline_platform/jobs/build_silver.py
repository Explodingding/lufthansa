"""Build cleaned silver datasets from source-aligned bronze Parquet datasets."""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    current_timestamp,
    greatest,
    lit,
    lower,
    round,
    unix_timestamp,
)

from airline_platform.jobs.parquet_io import (
    read_parquet_dataset,
    reset_output_dir,
    should_use_local_parquet_writer,
    write_parquet_dataset,
)

SILVER_SOURCES = ("flights", "airports", "weather", "passenger_events")


@dataclass(frozen=True)
class SourceSilverSummary:
    """Silver build outcome for one source dataset."""

    source: str
    input_path: str
    output_path: str
    record_count: int


@dataclass(frozen=True)
class SilverBuildSummary:
    """Summary produced by the silver build job."""

    bronze_dir: str
    output_dir: str
    sources: list[SourceSilverSummary]

    @property
    def total_records(self) -> int:
        """Return total silver record count across all sources."""

        return sum(source.record_count for source in self.sources)


def build_silver_layer(
    bronze_dir: Path,
    output_dir: Path,
    spark: SparkSession | None = None,
) -> SilverBuildSummary:
    """Read bronze Parquet datasets and write cleaned silver Parquet datasets."""

    owns_spark = spark is None
    active_spark = spark or _create_spark_session()

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        summaries: list[SourceSilverSummary] = []

        for source in SILVER_SOURCES:
            input_path = bronze_dir / source
            if not input_path.exists():
                message = f"Missing bronze source dataset: {input_path}"
                raise FileNotFoundError(message)

            output_path = output_dir / source

            if should_use_local_parquet_writer():
                silver_frame = _clean_source_pandas(source, pd.read_parquet(input_path))
                record_count = len(silver_frame)
                _write_pandas_parquet_dataset(silver_frame, output_path)
            else:
                bronze_frame = read_parquet_dataset(active_spark, input_path)
                silver_frame = _clean_source_frame(source, bronze_frame)
                record_count = silver_frame.count()
                write_parquet_dataset(silver_frame, output_path)

            summaries.append(
                SourceSilverSummary(
                    source=source,
                    input_path=str(input_path),
                    output_path=str(output_path),
                    record_count=record_count,
                )
            )

        summary = SilverBuildSummary(
            bronze_dir=str(bronze_dir),
            output_dir=str(output_dir),
            sources=summaries,
        )
        _write_summary(summary, output_dir)
        return summary
    finally:
        if owns_spark:
            active_spark.stop()


def main() -> None:
    """Run silver build from the command line."""

    parser = argparse.ArgumentParser(
        description="Build cleaned silver Parquet datasets from bronze datasets."
    )
    parser.add_argument(
        "--bronze-dir",
        type=Path,
        default=Path("data/bronze"),
        help="Directory containing bronze Parquet datasets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/silver"),
        help="Directory where silver Parquet datasets will be written.",
    )
    args = parser.parse_args()

    summary = build_silver_layer(args.bronze_dir, args.output_dir)
    print(f"Silver build finished: {summary.total_records} records.")


def _clean_source_frame(source: str, frame: DataFrame) -> DataFrame:
    if source == "flights":
        return _clean_flights(frame)
    if source == "airports":
        return _clean_airports(frame)
    if source == "weather":
        return _clean_weather(frame)
    if source == "passenger_events":
        return _clean_passenger_events(frame)

    message = f"Unsupported silver source: {source}"
    raise ValueError(message)


def _clean_source_pandas(source: str, frame: pd.DataFrame) -> pd.DataFrame:
    if source == "flights":
        return _clean_flights_pandas(frame)
    if source == "airports":
        return _clean_with_pandas_dedup(frame, ["airport_code"])
    if source == "weather":
        return _clean_with_pandas_dedup(frame, ["airport_code", "observed_at_utc"])
    if source == "passenger_events":
        return _clean_with_pandas_dedup(frame, ["event_id"])

    message = f"Unsupported silver source: {source}"
    raise ValueError(message)


def _clean_flights(frame: DataFrame) -> DataFrame:
    return (
        frame.dropDuplicates(["flight_id"])
        .withColumn("status", lower(col("status")))
        .withColumn(
            "departure_delay_minutes",
            round(
                (
                    unix_timestamp(col("actual_departure_utc"))
                    - unix_timestamp(col("scheduled_departure_utc"))
                )
                / 60,
                2,
            ),
        )
        .withColumn("departure_delay_minutes", greatest(col("departure_delay_minutes"), lit(0.0)))
        .withColumn("is_cancelled", col("status") == lit("cancelled"))
        .withColumn("is_delayed", col("departure_delay_minutes") > lit(15.0))
        .withColumn("_silver_loaded_at_utc", current_timestamp())
    )


def _clean_flights_pandas(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.drop_duplicates(subset=["flight_id"]).copy()
    cleaned["status"] = cleaned["status"].str.lower()
    scheduled = pd.to_datetime(cleaned["scheduled_departure_utc"], utc=True)
    actual = pd.to_datetime(cleaned["actual_departure_utc"], utc=True)
    cleaned["departure_delay_minutes"] = ((actual - scheduled).dt.total_seconds() / 60).round(2)
    cleaned["departure_delay_minutes"] = cleaned["departure_delay_minutes"].clip(lower=0)
    cleaned["is_cancelled"] = cleaned["status"] == "cancelled"
    cleaned["is_delayed"] = cleaned["departure_delay_minutes"] > 15.0
    cleaned["_silver_loaded_at_utc"] = pd.Timestamp.now(tz="UTC")
    return cleaned


def _clean_airports(frame: DataFrame) -> DataFrame:
    return frame.dropDuplicates(["airport_code"]).withColumn(
        "_silver_loaded_at_utc",
        current_timestamp(),
    )


def _clean_weather(frame: DataFrame) -> DataFrame:
    return frame.dropDuplicates(["airport_code", "observed_at_utc"]).withColumn(
        "_silver_loaded_at_utc", current_timestamp()
    )


def _clean_passenger_events(frame: DataFrame) -> DataFrame:
    return frame.dropDuplicates(["event_id"]).withColumn(
        "_silver_loaded_at_utc",
        current_timestamp(),
    )


def _clean_with_pandas_dedup(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    cleaned = frame.drop_duplicates(subset=keys).copy()
    cleaned["_silver_loaded_at_utc"] = pd.Timestamp.now(tz="UTC")
    return cleaned


def _write_pandas_parquet_dataset(frame: pd.DataFrame, output_path: Path) -> None:
    reset_output_dir(output_path)
    frame.to_parquet(output_path / "part-00000.parquet", index=False)


def _write_summary(summary: SilverBuildSummary, output_dir: Path) -> None:
    summary_dir = output_dir / "_build_summary"
    reset_output_dir(summary_dir)
    with (summary_dir / "summary.json").open("w", encoding="utf-8") as file:
        json.dump(asdict(summary), file, indent=2, sort_keys=True)
        file.write("\n")


def _create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("airline-silver-build")
        .master("local[1]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


if __name__ == "__main__":
    main()

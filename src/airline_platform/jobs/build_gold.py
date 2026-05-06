"""Build business-ready gold tables from cleaned silver datasets."""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    concat_ws,
    count,
    current_timestamp,
)
from pyspark.sql.functions import (
    sum as spark_sum,
)

from airline_platform.jobs.parquet_io import (
    read_parquet_dataset,
    reset_output_dir,
    should_use_local_parquet_writer,
    write_parquet_dataset,
)

GOLD_TABLES = (
    "gold_flight_performance",
    "gold_route_performance",
    "gold_airport_disruption",
    "gold_passenger_communication",
)


@dataclass(frozen=True)
class GoldTableSummary:
    """Gold build outcome for one business table."""

    table: str
    output_path: str
    record_count: int


@dataclass(frozen=True)
class GoldBuildSummary:
    """Summary produced by the gold build job."""

    silver_dir: str
    output_dir: str
    tables: list[GoldTableSummary]

    @property
    def total_records(self) -> int:
        """Return total gold record count across all tables."""

        return sum(table.record_count for table in self.tables)


def build_gold_layer(
    silver_dir: Path,
    output_dir: Path,
    spark: SparkSession | None = None,
) -> GoldBuildSummary:
    """Read silver datasets and write business-ready gold Parquet tables."""

    owns_spark = spark is None
    active_spark = spark or _create_spark_session()

    try:
        _ensure_silver_inputs_exist(silver_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if should_use_local_parquet_writer():
            tables = _build_gold_tables_pandas(silver_dir)
            summaries = _write_gold_tables_pandas(tables, output_dir)
        else:
            tables = _build_gold_tables_spark(active_spark, silver_dir)
            summaries = _write_gold_tables_spark(tables, output_dir)

        summary = GoldBuildSummary(
            silver_dir=str(silver_dir),
            output_dir=str(output_dir),
            tables=summaries,
        )
        _write_summary(summary, output_dir)
        return summary
    finally:
        if owns_spark:
            active_spark.stop()


def main() -> None:
    """Run gold build from the command line."""

    parser = argparse.ArgumentParser(
        description="Build business-ready gold Parquet tables from silver datasets."
    )
    parser.add_argument(
        "--silver-dir",
        type=Path,
        default=Path("data/silver"),
        help="Directory containing silver Parquet datasets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/gold"),
        help="Directory where gold Parquet tables will be written.",
    )
    args = parser.parse_args()

    summary = build_gold_layer(args.silver_dir, args.output_dir)
    print(f"Gold build finished: {summary.total_records} records.")


def _build_gold_tables_pandas(silver_dir: Path) -> dict[str, pd.DataFrame]:
    flights = pd.read_parquet(silver_dir / "flights")
    airports = pd.read_parquet(silver_dir / "airports")
    weather = pd.read_parquet(silver_dir / "weather")
    passenger_events = pd.read_parquet(silver_dir / "passenger_events")

    flight_performance = _gold_flight_performance_pandas(flights, airports, weather)
    return {
        "gold_flight_performance": flight_performance,
        "gold_route_performance": _gold_route_performance_pandas(flight_performance),
        "gold_airport_disruption": _gold_airport_disruption_pandas(
            flight_performance,
            airports,
        ),
        "gold_passenger_communication": _gold_passenger_communication_pandas(
            passenger_events,
            flight_performance,
        ),
    }


def _gold_flight_performance_pandas(
    flights: pd.DataFrame,
    airports: pd.DataFrame,
    weather: pd.DataFrame,
) -> pd.DataFrame:
    origin_airports = airports.add_prefix("origin_")
    destination_airports = airports.add_prefix("destination_")
    weather_by_airport = (
        weather.sort_values("observed_at_utc")
        .drop_duplicates(subset=["airport_code"])
        .rename(
            columns={
                "airport_code": "origin_airport",
                "temperature_c": "origin_temperature_c",
                "wind_speed_kmh": "origin_wind_speed_kmh",
                "precipitation_mm": "origin_precipitation_mm",
            }
        )
    )

    result = flights.merge(
        origin_airports,
        left_on="origin_airport",
        right_on="origin_airport_code",
        how="left",
    ).merge(
        destination_airports,
        left_on="destination_airport",
        right_on="destination_airport_code",
        how="left",
    )
    result = result.merge(weather_by_airport, on="origin_airport", how="left")
    result["route"] = result["origin_airport"] + "-" + result["destination_airport"]
    result["_gold_loaded_at_utc"] = pd.Timestamp.now(tz="UTC")
    return result


def _gold_route_performance_pandas(flight_performance: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        flight_performance.groupby("route", dropna=False)
        .agg(
            total_flights=("flight_id", "count"),
            delayed_flights=("is_delayed", "sum"),
            cancelled_flights=("is_cancelled", "sum"),
            average_departure_delay_minutes=("departure_delay_minutes", "mean"),
        )
        .reset_index()
    )
    grouped["delay_rate"] = grouped["delayed_flights"] / grouped["total_flights"]
    grouped["_gold_loaded_at_utc"] = pd.Timestamp.now(tz="UTC")
    return grouped


def _gold_airport_disruption_pandas(
    flight_performance: pd.DataFrame,
    airports: pd.DataFrame,
) -> pd.DataFrame:
    grouped = (
        flight_performance.groupby("origin_airport", dropna=False)
        .agg(
            total_departures=("flight_id", "count"),
            delayed_departures=("is_delayed", "sum"),
            cancelled_departures=("is_cancelled", "sum"),
            average_departure_delay_minutes=("departure_delay_minutes", "mean"),
        )
        .reset_index()
    )
    grouped["delay_rate"] = grouped["delayed_departures"] / grouped["total_departures"]
    grouped = grouped.merge(airports, left_on="origin_airport", right_on="airport_code", how="left")
    grouped["_gold_loaded_at_utc"] = pd.Timestamp.now(tz="UTC")
    return grouped


def _gold_passenger_communication_pandas(
    passenger_events: pd.DataFrame,
    flight_performance: pd.DataFrame,
) -> pd.DataFrame:
    events_with_flights = passenger_events.merge(
        flight_performance[["flight_id", "route", "status", "is_delayed", "is_cancelled"]],
        on="flight_id",
        how="left",
    )
    grouped = (
        events_with_flights.groupby(["event_type", "channel", "route"], dropna=False)
        .agg(
            event_count=("event_id", "count"),
            delayed_flight_events=("is_delayed", "sum"),
            cancelled_flight_events=("is_cancelled", "sum"),
        )
        .reset_index()
    )
    grouped["_gold_loaded_at_utc"] = pd.Timestamp.now(tz="UTC")
    return grouped


def _build_gold_tables_spark(
    spark: SparkSession,
    silver_dir: Path,
) -> dict[str, DataFrame]:
    flights = read_parquet_dataset(spark, silver_dir / "flights")
    airports = read_parquet_dataset(spark, silver_dir / "airports")
    weather = read_parquet_dataset(spark, silver_dir / "weather")
    passenger_events = read_parquet_dataset(spark, silver_dir / "passenger_events")

    flight_performance = _gold_flight_performance_spark(flights, airports, weather)
    return {
        "gold_flight_performance": flight_performance,
        "gold_route_performance": _gold_route_performance_spark(flight_performance),
        "gold_airport_disruption": _gold_airport_disruption_spark(flight_performance, airports),
        "gold_passenger_communication": _gold_passenger_communication_spark(
            passenger_events,
            flight_performance,
        ),
    }


def _gold_flight_performance_spark(
    flights: DataFrame,
    airports: DataFrame,
    weather: DataFrame,
) -> DataFrame:
    origin_airports = airports.select(
        *(col(column).alias(f"origin_{column}") for column in airports.columns)
    )
    destination_airports = airports.select(
        *(col(column).alias(f"destination_{column}") for column in airports.columns)
    )
    weather_by_airport = weather.dropDuplicates(["airport_code"]).select(
        col("airport_code").alias("origin_airport"),
        col("temperature_c").alias("origin_temperature_c"),
        col("wind_speed_kmh").alias("origin_wind_speed_kmh"),
        col("precipitation_mm").alias("origin_precipitation_mm"),
    )

    return (
        flights.join(
            origin_airports,
            flights.origin_airport == origin_airports.origin_airport_code,
            "left",
        )
        .join(
            destination_airports,
            flights.destination_airport == destination_airports.destination_airport_code,
            "left",
        )
        .join(weather_by_airport, on="origin_airport", how="left")
        .withColumn("route", concat_ws("-", col("origin_airport"), col("destination_airport")))
        .withColumn("_gold_loaded_at_utc", current_timestamp())
    )


def _gold_route_performance_spark(flight_performance: DataFrame) -> DataFrame:
    return (
        flight_performance.groupBy("route")
        .agg(
            count("flight_id").alias("total_flights"),
            spark_sum(col("is_delayed").cast("int")).alias("delayed_flights"),
            spark_sum(col("is_cancelled").cast("int")).alias("cancelled_flights"),
            avg("departure_delay_minutes").alias("average_departure_delay_minutes"),
        )
        .withColumn("delay_rate", col("delayed_flights") / col("total_flights"))
        .withColumn("_gold_loaded_at_utc", current_timestamp())
    )


def _gold_airport_disruption_spark(
    flight_performance: DataFrame,
    airports: DataFrame,
) -> DataFrame:
    grouped = (
        flight_performance.groupBy("origin_airport")
        .agg(
            count("flight_id").alias("total_departures"),
            spark_sum(col("is_delayed").cast("int")).alias("delayed_departures"),
            spark_sum(col("is_cancelled").cast("int")).alias("cancelled_departures"),
            avg("departure_delay_minutes").alias("average_departure_delay_minutes"),
        )
        .withColumn("delay_rate", col("delayed_departures") / col("total_departures"))
    )
    return grouped.join(
        airports, grouped.origin_airport == airports.airport_code, "left"
    ).withColumn("_gold_loaded_at_utc", current_timestamp())


def _gold_passenger_communication_spark(
    passenger_events: DataFrame,
    flight_performance: DataFrame,
) -> DataFrame:
    events_with_flights = passenger_events.join(
        flight_performance.select("flight_id", "route", "status", "is_delayed", "is_cancelled"),
        on="flight_id",
        how="left",
    )
    return (
        events_with_flights.groupBy("event_type", "channel", "route")
        .agg(
            count("event_id").alias("event_count"),
            spark_sum(col("is_delayed").cast("int")).alias("delayed_flight_events"),
            spark_sum(col("is_cancelled").cast("int")).alias("cancelled_flight_events"),
        )
        .withColumn("_gold_loaded_at_utc", current_timestamp())
    )


def _write_gold_tables_pandas(
    tables: dict[str, pd.DataFrame],
    output_dir: Path,
) -> list[GoldTableSummary]:
    summaries: list[GoldTableSummary] = []
    for table_name in GOLD_TABLES:
        table = tables[table_name]
        output_path = output_dir / table_name
        reset_output_dir(output_path)
        table.to_parquet(output_path / "part-00000.parquet", index=False)
        summaries.append(
            GoldTableSummary(
                table=table_name,
                output_path=str(output_path),
                record_count=len(table),
            )
        )

    return summaries


def _write_gold_tables_spark(
    tables: dict[str, DataFrame],
    output_dir: Path,
) -> list[GoldTableSummary]:
    summaries: list[GoldTableSummary] = []
    for table_name in GOLD_TABLES:
        table = tables[table_name]
        output_path = output_dir / table_name
        record_count = table.count()
        write_parquet_dataset(table, output_path)
        summaries.append(
            GoldTableSummary(
                table=table_name,
                output_path=str(output_path),
                record_count=record_count,
            )
        )

    return summaries


def _write_summary(summary: GoldBuildSummary, output_dir: Path) -> None:
    summary_dir = output_dir / "_build_summary"
    reset_output_dir(summary_dir)
    with (summary_dir / "summary.json").open("w", encoding="utf-8") as file:
        json.dump(asdict(summary), file, indent=2, sort_keys=True)
        file.write("\n")


def _ensure_silver_inputs_exist(silver_dir: Path) -> None:
    required_sources = ("flights", "airports", "weather", "passenger_events")
    for source in required_sources:
        input_path = silver_dir / source
        if not input_path.exists():
            message = f"Missing silver source dataset: {input_path}"
            raise FileNotFoundError(message)


def _create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("airline-gold-build")
        .master("local[1]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


if __name__ == "__main__":
    main()

"""Build the bronze layer from validated raw JSON source files."""

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name
from pyspark.sql.types import DoubleType, StringType, StructField, StructType, TimestampType

from airline_platform.contracts import SourceContract, get_contract

BRONZE_SOURCES = (
    SourceContract.FLIGHTS,
    SourceContract.AIRPORTS,
    SourceContract.WEATHER,
    SourceContract.PASSENGER_EVENTS,
)


@dataclass(frozen=True)
class SourceBronzeSummary:
    """Bronze build outcome for one source dataset."""

    source: str
    input_path: str
    output_path: str
    record_count: int


@dataclass(frozen=True)
class BronzeBuildSummary:
    """Summary produced by the bronze build job."""

    raw_dir: str
    output_dir: str
    sources: list[SourceBronzeSummary]

    @property
    def total_records(self) -> int:
        """Return total bronze record count across all sources."""

        return sum(source.record_count for source in self.sources)


def build_bronze_layer(
    raw_dir: Path,
    output_dir: Path,
    spark: SparkSession | None = None,
) -> BronzeBuildSummary:
    """Read validated raw JSON files and write source-aligned bronze Parquet datasets."""

    owns_spark = spark is None
    active_spark = spark or _create_spark_session()

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        summaries: list[SourceBronzeSummary] = []

        for source in BRONZE_SOURCES:
            input_path = raw_dir / f"{source.value}.json"
            if not input_path.exists():
                message = f"Missing raw source file: {input_path}"
                raise FileNotFoundError(message)

            bronze_frame = _read_raw_source(active_spark, input_path, source)
            output_path = output_dir / source.value
            record_count = bronze_frame.count()

            _write_bronze_frame(bronze_frame, output_path)
            summaries.append(
                SourceBronzeSummary(
                    source=source.value,
                    input_path=str(input_path),
                    output_path=str(output_path),
                    record_count=record_count,
                )
            )

        summary = BronzeBuildSummary(
            raw_dir=str(raw_dir),
            output_dir=str(output_dir),
            sources=summaries,
        )
        _write_summary(summary, output_dir)
        return summary
    finally:
        if owns_spark:
            active_spark.stop()


def main() -> None:
    """Run bronze build from the command line."""

    parser = argparse.ArgumentParser(
        description="Build bronze Parquet datasets from raw JSON files."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing raw JSON source files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/bronze"),
        help="Directory where bronze Parquet datasets will be written.",
    )
    args = parser.parse_args()

    summary = build_bronze_layer(args.raw_dir, args.output_dir)
    print(f"Bronze build finished: {summary.total_records} records.")


def _read_raw_source(spark: SparkSession, input_path: Path, source: SourceContract) -> DataFrame:
    schema = _spark_schema_for(source)
    return (
        spark.read.option("multiLine", "true")
        .schema(schema)
        .json(str(input_path))
        .withColumn("_bronze_loaded_at_utc", current_timestamp())
        .withColumn("_source_file", input_file_name())
    )


def _spark_schema_for(source: SourceContract) -> StructType:
    fields = []
    for contract_field in get_contract(source):
        fields.append(
            StructField(
                contract_field.name,
                _spark_type_for(contract_field.dtype),
                nullable=not contract_field.required,
            )
        )

    return StructType(fields)


def _spark_type_for(dtype: str):
    if dtype == "timestamp":
        return TimestampType()
    if dtype == "float":
        return DoubleType()
    return StringType()


def _write_summary(
    summary: BronzeBuildSummary,
    output_dir: Path,
) -> None:
    summary_dir = output_dir / "_build_summary"
    _reset_output_dir(summary_dir)
    with (summary_dir / "summary.json").open("w", encoding="utf-8") as file:
        json.dump(asdict(summary), file, indent=2, sort_keys=True)
        file.write("\n")


def _write_bronze_frame(frame: DataFrame, output_path: Path) -> None:
    _reset_output_dir(output_path)

    if _should_use_local_parquet_writer():
        frame.toPandas().to_parquet(output_path / "part-00000.parquet", index=False)
        return

    frame.write.mode("overwrite").parquet(str(output_path))


def _reset_output_dir(output_path: Path) -> None:
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)


def _should_use_local_parquet_writer() -> bool:
    return os.name == "nt" and not os.environ.get("HADOOP_HOME")


def _create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("airline-bronze-build")
        .master("local[1]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


if __name__ == "__main__":
    main()

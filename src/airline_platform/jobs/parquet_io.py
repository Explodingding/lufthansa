"""Shared Parquet IO helpers for local and Spark-friendly pipeline jobs."""

import os
import shutil
from pathlib import Path

import pandas as pd
from pyspark.sql import DataFrame, SparkSession


def read_parquet_dataset(spark: SparkSession, input_path: Path) -> DataFrame:
    """Read a Parquet dataset with Windows-friendly fallback."""

    if should_use_local_parquet_writer():
        pandas_frame = pd.read_parquet(input_path)
        return spark.createDataFrame(pandas_frame)

    return spark.read.parquet(str(input_path))


def write_parquet_dataset(frame: DataFrame, output_path: Path) -> None:
    """Write a Spark DataFrame as a Parquet dataset with Windows-friendly fallback."""

    reset_output_dir(output_path)

    if should_use_local_parquet_writer():
        frame.toPandas().to_parquet(output_path / "part-00000.parquet", index=False)
        return

    frame.write.mode("overwrite").parquet(str(output_path))


def reset_output_dir(output_path: Path) -> None:
    """Remove and recreate an output directory."""

    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)


def should_use_local_parquet_writer() -> bool:
    """Return true when local Spark Parquet writes need a Windows fallback."""

    return os.name == "nt" and not os.environ.get("HADOOP_HOME")

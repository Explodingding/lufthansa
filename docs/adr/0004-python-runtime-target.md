# ADR 0004: Python Runtime Target

## Status

Accepted

## Context

Python 3.14.4 is the latest stable CPython release at the time of writing. The local workstation may also have newer Python versions installed, but the project depends on PySpark and is intended to map cleanly to Azure Databricks, so the runtime cannot be selected only by the latest local Python release.

Databricks Runtime 16.4 LTS is powered by Apache Spark 3.5.2. Python 3.13 support starts in upstream Spark 4.x, but choosing it would make the project depend on newer Databricks Runtime behavior and less familiar tooling assumptions. Python 3.14 is not selected as the project runtime until Spark, Databricks-oriented tooling, and the wider data stack clearly support it.

## Decision

Target Python 3.12 for local development and CI, while allowing Python 3.11 through 3.12 in package metadata.

The project pins PySpark to 3.5.2 to align with Databricks Runtime 16.4 LTS. Runtime data dependencies also keep conservative major-version bounds so local installs do not silently drift to newer, untested Pandas, NumPy, or PyArrow major versions.

## Consequences

This prioritizes Databricks compatibility over the newest local Python version. The current workstation should use a Python 3.12 virtual environment for fully representative local development; Python 3.13 may still run simple non-Spark unit tests, but it is not the declared project target.
# Airline Digital Experience Data Platform

Portfolio data engineering project inspired by Lufthansa Group Digital Hangar and Middleware collaboration.

The goal is to build a small but production-minded data product: extract airline and travel-experience data from API-like sources, land it in a data lake, process it with PySpark, validate data quality with tests, expose SQL-ready analytical tables, and present insights in a dashboard.

## Why This Project

The project is designed around a Data Engineer role that combines data processing pipelines, dataset exploration, dashboards, API extraction, modern data architecture, Azure Data Factory, Databricks, and agile engineering practices.

Instead of presenting only a CV, this repository demonstrates how I would approach a real data product from scratch:

- define data contracts with a Middleware-facing mindset,
- build clean and testable Python/PySpark code,
- structure the pipeline as a bronze/silver/gold data lake,
- validate transformations with `pytest`,
- enforce code quality with `ruff`,
- prepare CI checks for review-ready development,
- show business value through notebooks, SQL, and a Streamlit dashboard.

## Business Scenario

Middleware exposes flight, airport, weather, and passenger-event data through APIs and operational files. Digital Hangar product teams need reliable insights to understand disruptions, punctuality, route performance, and the impact of operational events on the digital travel experience.

This platform turns raw operational signals into curated analytical data products that can support product owners, business analysts, data scientists, and engineering teams.

## Target Architecture

```mermaid
flowchart LR
    middlewareApis["Middleware APIs and Files"] --> apiExtractor["Python API Extractor"]
    apiExtractor --> rawLayer["Raw Layer: JSON or CSV"]
    rawLayer --> bronzeLayer["Bronze Layer: Ingested Data"]
    bronzeLayer --> silverLayer["Silver Layer: Cleaned Parquet"]
    silverLayer --> qualityChecks["pytest Data Quality Checks"]
    qualityChecks --> goldLayer["Gold Layer: Analytics Tables"]
    goldLayer --> sqlInsights["SQL Insights"]
    goldLayer --> streamlitDashboard["Streamlit Dashboard"]
    goldLayer --> explorationNotebook["Pandas and NumPy Exploration"]

    adfBlueprint["Azure Data Factory Blueprint"] --> apiExtractor
    databricksBlueprint["Databricks Job Blueprint"] --> bronzeLayer
```

## Planned Stack

- Python, Pandas, NumPy
- PySpark
- SQL
- pytest
- Ruff
- Streamlit
- GitHub Actions
- Azure Data Factory blueprint
- Databricks job/notebook blueprint

## Repository Structure

```text
cloud/                  Azure Data Factory and Databricks blueprints
dashboard/              Streamlit dashboard
data/                   Local data lake folders
docs/                   Architecture, team context, ADRs, acceptance criteria
notebooks/              Exploratory analysis
scripts/                Local developer commands
sql/                    Analytical queries
src/airline_platform/   Python package
tests/                  Unit and data quality tests
```

## Development Commands

Use Python 3.11 or 3.12 for local development. This matches the intended PySpark and Databricks-oriented runtime.

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format .
pytest
```

On Windows PowerShell:

```powershell
.\scripts\run_checks.ps1
```

## Current Status

Day 1 foundation is in progress:

- repository structure,
- project narrative,
- data contracts,
- clean code tooling,
- first tests and CI workflow.


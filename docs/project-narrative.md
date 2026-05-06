# Project Narrative

## One-Sentence Pitch

Airline Digital Experience Data Platform is a portfolio data engineering project that turns airline operational signals from Middleware-style sources into curated data lake tables, SQL insights, and a Digital Hangar-facing dashboard.

## The Problem

Airline digital products depend on many operational signals: flight status, airport context, disruption events, weather, and passenger communication events. These signals often come from different source systems and arrive through integration layers, APIs, or operational files.

For a Digital Hangar product team, raw operational data is not enough. Product owners, business analysts, and data scientists need cleaned, validated, and understandable datasets that can answer questions such as:

- Which routes are most affected by delays?
- Are disruption notifications sent at the right time?
- Which airports or weather patterns correlate with poor punctuality?
- What operational signals should be exposed in a passenger-facing digital experience?

This project treats those questions as a small data product rather than a one-off script.

## The Product Idea

The platform simulates a collaboration between two sides of the organization:

- Middleware provides access to operational data through APIs and source-aligned payloads.
- Digital Hangar consumes curated data products to improve customer-facing digital travel experiences.

The project ingests raw source data, preserves it for traceability, transforms it through bronze, silver, and gold layers, validates important assumptions with tests, and exposes insights through SQL, notebooks, and a dashboard.

## Why This Is Relevant To The Role

The role requires delivering high-quality data processing pipelines, exploring datasets, and creating dashboards while working with Middleware and Digital Hangar teams. This repository is designed to mirror that responsibility:

- API extraction is represented by extractor modules and source contracts.
- Data understanding is represented by explicit schemas, tests, and planned exploration notebooks.
- Data cleaning and processing are represented by the bronze, silver, and gold data lake design.
- Dashboarding is represented by the planned Streamlit application.
- Engineering quality is represented by Ruff, pytest, CI, ADRs, and code review documentation.
- Cloud readiness is represented by Azure Data Factory and Databricks blueprints.

## Design Principles

### Build Locally, Map To Cloud

The project must run locally so that a reviewer can inspect it without Azure credentials. At the same time, the architecture is intentionally shaped so it can be mapped to Azure Data Factory orchestration and Databricks processing.

### Preserve Raw Data

Raw source payloads should be stored before cleaning. This keeps the pipeline traceable and gives the data engineering process a clear boundary between ingestion and transformation.

### Prefer Explicit Contracts

Source contracts make assumptions visible. This is important when working with Middleware or API-provided data because downstream processing should fail clearly when required fields disappear.

### Test Business Rules

The project uses tests not only for code correctness, but also for data quality rules: required fields, relationships between events and flights, and transformation expectations.

### Keep Versions Stable

The target stack is intentionally frozen for the project duration. Python 3.12 and PySpark 3.5.2 are selected to align with Databricks Runtime 16.4 LTS rather than chasing the newest local Python release.

## Intended Demo Flow

1. Read the README to understand the business scenario.
2. Inspect data contracts and acceptance criteria.
3. Run local quality checks.
4. Generate or extract raw data.
5. Run data lake transformations.
6. Query gold tables with SQL.
7. Open the dashboard and review Digital Hangar-facing metrics.
8. Review cloud blueprints to understand how the local pipeline maps to ADF and Databricks.

## What The Project Should Prove

This project should prove that I can think beyond a single script or notebook. It shows that I can structure a small data product from scratch, make engineering decisions explicit, keep quality gates visible, and connect technical implementation to business questions.
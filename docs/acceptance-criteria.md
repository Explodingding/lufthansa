# Acceptance Criteria

## MVP Goal

Build a local, review-ready data engineering project that demonstrates API extraction, modern data lake processing, data cleaning, analysis, dashboarding, testing, and CI/CD.

## User Stories

### Middleware Integration

As a Middleware-facing data engineer, I want to ingest API-like airline data into a raw landing zone so that downstream processing can preserve traceability and avoid coupling directly to source systems.

Acceptance criteria:

- raw payloads are stored without destructive transformations,
- each source has an explicit schema contract,
- ingestion can fall back to synthetic data if a public API is unavailable,
- tests verify expected input fields and data types.

### Data Lake Processing

As a data engineer, I want to transform raw operational data into bronze, silver, and gold layers so that business users receive clean and analytics-ready datasets.

Acceptance criteria:

- bronze keeps source-aligned ingested data,
- silver contains cleaned and deduplicated records,
- gold contains business-level tables for reporting,
- transformation logic is covered by unit tests,
- outputs are stored in local data lake folders.

### Digital Hangar Analytics

As a Digital Hangar product owner, I want to see flight disruption and punctuality metrics so that the team can reason about the digital travel experience.

Acceptance criteria:

- dashboard shows key metrics for punctuality, disruption, and route performance,
- SQL queries answer at least three product or operations questions,
- notebook documents initial data understanding and quality observations.

### Engineering Quality

As a reviewer, I want the project to follow clean code and CI practices so that it is easy to review and extend.

Acceptance criteria:

- `ruff check .` passes,
- `ruff format --check .` passes in CI,
- `pytest` passes,
- code is split into small modules with explicit responsibilities,
- code review checklist is present.


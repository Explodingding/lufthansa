# MVP Backlog And Acceptance Criteria

## MVP Goal

Build a local, review-ready data engineering project that demonstrates API extraction, modern data lake processing, data cleaning, analysis, dashboarding, testing, and CI/CD. The final project should be understandable to a recruiter, useful for a technical interviewer, and credible for a Databricks/Azure-oriented data engineering role.

## Definition Of Done

The MVP is done when:

- the project can be installed and checked locally,
- source contracts are documented and tested,
- raw data can be created from a public API path or synthetic fallback,
- raw data is transformed into bronze, silver, and gold layers,
- important transformation and data quality rules are covered by tests,
- SQL queries answer defined business questions,
- a Streamlit dashboard presents clear Digital Hangar-facing metrics,
- the README explains the business context, architecture, commands, and demo flow,
- CI runs linting, formatting checks, and tests,
- cloud blueprints explain how the local flow maps to Azure Data Factory and Databricks.

## Must Have Scope

These items are required for the recruitment-ready version.

### Epic 1: Middleware-Style Data Ingestion

User story:

As a Middleware-facing data engineer, I want to ingest API-like airline data into a raw landing zone so that downstream processing can preserve traceability and avoid coupling directly to source systems.

Acceptance criteria:

- raw payloads are stored without destructive transformations,
- each source has an explicit schema contract,
- ingestion can fall back to synthetic data if a public API is unavailable,
- input validation returns human-readable errors,
- tests verify expected input fields and required relationships,
- raw output can be regenerated with one documented command.

Deliverables:

- extractor interface,
- synthetic fallback writer,
- raw JSON or CSV files,
- validation summary.

### Epic 2: Data Lake Processing

User story:

As a data engineer, I want to transform raw operational data into bronze, silver, and gold layers so that business users receive clean and analytics-ready datasets.

Acceptance criteria:

- bronze keeps source-aligned ingested data,
- silver contains cleaned and deduplicated records,
- gold contains business-level tables for reporting,
- transformation logic is covered by unit tests,
- outputs are stored in local data lake folders,
- pipeline behavior is deterministic and repeatable.

Deliverables:

- PySpark jobs for bronze, silver, and gold layers,
- local Parquet outputs,
- transformation tests,
- documented pipeline command.

### Epic 3: Data Understanding And Analysis

User story:

As a data analyst or data scientist, I want to explore the source and cleaned datasets so that I can understand data quality, distributions, and useful business metrics before building the dashboard.

Acceptance criteria:

- notebook documents the available datasets,
- notebook includes missing value and duplicate checks,
- notebook explains at least three business observations,
- Pandas and NumPy are used where appropriate,
- findings influence dashboard metric selection.

Deliverables:

- exploratory notebook,
- short summary of findings,
- candidate metric definitions.

### Epic 4: Digital Hangar Dashboard

User story:

As a Digital Hangar product owner, I want to see flight disruption and punctuality metrics so that the team can reason about the digital travel experience.

Acceptance criteria:

- dashboard shows total flights, delayed flights, cancelled flights, delay rate, and average delay,
- dashboard shows route and airport disruption views,
- dashboard includes passenger communication event context,
- filters are understandable to non-engineering users,
- metric definitions are documented,
- dashboard can run locally without cloud credentials.

Deliverables:

- Streamlit dashboard,
- dashboard-ready gold tables,
- screenshot or demo notes for the README.

### Epic 5: SQL Insights

User story:

As a business analyst, I want SQL queries over gold-layer tables so that I can inspect metrics without reading pipeline code.

Acceptance criteria:

- SQL queries answer at least three product or operations questions,
- query names are descriptive,
- expected business meaning is documented,
- queries use gold-layer tables rather than raw inputs.

Deliverables:

- SQL files,
- documented questions,
- example outputs or expected interpretation.

### Epic 6: Engineering Quality

User story:

As a reviewer, I want the project to follow clean code and CI practices so that it is easy to review and extend.

Acceptance criteria:

- `ruff check .` passes,
- `ruff format --check .` passes,
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest` passes,
- CI runs all quality checks,
- code is split into small modules with explicit responsibilities,
- code review checklist is present,
- architectural decisions are captured in ADRs.

Deliverables:

- Ruff configuration,
- pytest suite,
- GitHub Actions workflow,
- code review checklist,
- ADRs.

### Epic 7: Cloud Blueprint

User story:

As an architect or data engineer, I want to understand how the local pipeline maps to Azure Data Factory and Databricks so that the project demonstrates cloud awareness without requiring paid cloud access.

Acceptance criteria:

- Azure Data Factory is described as orchestration,
- Databricks is described as compute for Spark processing,
- selected runtime target is documented,
- local steps are mapped to cloud steps,
- assumptions and limitations are explicit.

Deliverables:

- Azure Data Factory blueprint notes,
- Databricks blueprint notes,
- architecture diagram or mapping table.

## Should Have Scope

These items strengthen the project but are not required for the MVP:

- quarantine output for rejected records,
- generated sample data larger than the default demo dataset,
- dashboard screenshots in the README,
- simple data quality report file,
- GitHub pull request template,
- one example ADR for a transformation design decision.

## Out Of Scope

These items are intentionally excluded from the MVP:

- real passenger personal data,
- real Lufthansa internal data or systems,
- production Azure deployment,
- streaming architecture,
- machine learning predictions,
- complex authorization or secret management,
- perfect visual design for the dashboard.

## Completion Checklist

- [x] Repository structure exists.
- [x] Project narrative exists.
- [x] Initial data contracts exist.
- [x] Code quality tooling exists.
- [x] Initial tests exist.
- [x] Data ingestion writes raw files.
- [x] Validation summary is produced.
- [x] Public airport metadata extractor exists.
- [x] Public weather enrichment extractor exists.
- [x] Bronze layer is implemented.
- [x] Silver layer is implemented.
- [x] Gold layer is implemented.
- [ ] Exploratory notebook exists.
- [x] SQL insights exist.
- [ ] Streamlit dashboard exists.
- [ ] ADF blueprint is detailed.
- [ ] Databricks blueprint is detailed.
- [ ] README includes final demo flow.
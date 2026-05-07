# Demo Script

This script is a short guide for presenting the project in a recruitment process.

## 1. Opening Pitch

I prepared this project instead of relying only on a traditional CV. It is a compact data engineering product inspired by airline digital experience use cases and the collaboration between Middleware and Digital Hangar teams.

The project demonstrates API-style extraction, data contracts, a raw/bronze/silver/gold data lake, PySpark processing, SQL insights, exploratory analysis, a Streamlit dashboard, CI, and Azure Data Factory/Databricks cloud mapping.

## 2. What To Show First

Start with `README.md`:

- explain the business scenario,
- show the architecture diagram,
- mention the Databricks-compatible runtime target: Python 3.12 and PySpark 3.5.2,
- point to the final demo flow.

## 3. Pipeline Demo

Run or describe the local pipeline:

```powershell
airline-ingest-raw --output-dir data/raw
airline-build-bronze --raw-dir data/raw --output-dir data/bronze
airline-build-silver --bronze-dir data/bronze --output-dir data/silver
airline-build-gold --silver-dir data/silver --output-dir data/gold
```

Key message:

- raw keeps source-shaped validated data,
- bronze preserves source-aligned ingested datasets,
- silver cleans and deduplicates data,
- gold creates business-ready tables.

## 4. Data Understanding

Open:

- `notebooks/exploratory_analysis.ipynb`
- `docs/exploratory-analysis.md`

Highlight:

- missing value checks,
- duplicate checks,
- delay distribution,
- business observations that shaped the dashboard metrics.

## 5. SQL And Dashboard

Show SQL examples:

- `sql/route_delay_analysis.sql`
- `sql/airport_disruption_ranking.sql`
- `sql/passenger_communication_impact.sql`

Then run:

```powershell
streamlit run dashboard/app.py
```

Key message:

The dashboard uses gold-layer data and focuses on route disruption, airport impact, and passenger communication around disruptions.

## 6. Cloud Mapping

Show:

- `docs/cloud-blueprint.md`
- `cloud/adf/pipeline-blueprint.json`
- `cloud/databricks/job-blueprint.json`

Key message:

ADF is the orchestrator. Databricks is the Spark runtime. The local pipeline is intentionally shaped so it can map to cloud jobs without changing the data architecture.

## 7. Hosting Recommendation

For recruitment, the repository itself should remain the main artefact because it shows code quality, tests, CI, architecture, and documentation.

If a live dashboard is useful, the best fit is:

- Streamlit Community Cloud for the fastest Streamlit deployment,
- Render or Hugging Face Spaces for simple Python app hosting,
- Azure App Service or Azure Container Apps if you want to align strongly with the Azure theme.

Netlify is not the best host for the live Streamlit app because Netlify is primarily for static frontend sites. It can still be useful as a static landing page that links to GitHub and a hosted Streamlit app.

## 8. Closing Message

This project is intentionally small enough to review, but complete enough to show how I think about production-minded data engineering: contracts, data quality, testability, cloud mapping, and business-facing outputs.


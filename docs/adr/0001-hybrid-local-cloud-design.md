# ADR 0001: Hybrid Local And Cloud Design

## Status

Accepted

## Context

The project must be useful as a recruitment portfolio artifact and should not depend on paid cloud services or unavailable credentials. At the same time, the target role expects Azure Data Factory and Databricks experience.

## Decision

The implementation will run locally first and provide cloud blueprints for Azure Data Factory and Databricks.

Local execution will cover:

- API extraction or synthetic fallback,
- data lake folders,
- PySpark transformations,
- tests,
- SQL queries,
- dashboard.

Cloud blueprints will show how the same flow maps to:

- Azure Data Factory orchestration,
- Databricks jobs and notebooks,
- cloud object storage.

## Consequences

This keeps the project easy to review and run while still demonstrating cloud architecture thinking. The cloud part is intentionally a blueprint, not a hard runtime dependency.
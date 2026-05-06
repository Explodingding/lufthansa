# Code Review Checklist

Use this checklist to keep the project aligned with clean code, TDD, CI/CD, and data engineering quality expectations.

## Python Quality

- Functions have one clear responsibility.
- Names describe business meaning, not only technical mechanics.
- Public functions include type hints.
- Errors are handled close to the boundary where they can happen.
- No secrets, credentials, or API keys are committed.

## Data Engineering Quality

- Source data contracts are explicit.
- Raw data is preserved before cleaning.
- Transformations are deterministic and idempotent.
- Deduplication rules are documented.
- Date and time handling is explicit.
- Gold tables answer defined business questions.

## Testing

- Tests cover important transformation rules.
- Tests include data quality expectations.
- API contract tests cover required fields.
- Edge cases are represented with small fixtures.
- Tests can run locally without cloud access.

## CI/CD Readiness

- `ruff check .` passes.
- `ruff format --check .` passes.
- `pytest` passes.
- The README documents local commands.
- The change is small enough to review.


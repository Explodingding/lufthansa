# ADR 0003: Ruff For Code Quality

## Status

Accepted

## Context

The job description emphasizes clean code, code review, unit tests, CI/CD, and modern development practices. The project needs a lightweight way to enforce Python quality locally and in CI.

## Decision

Use Ruff for linting and formatting.

Ruff is selected because it is fast, simple to configure, and covers many checks that would otherwise require multiple tools.

## Consequences

Developers can run:

```bash
ruff check .
ruff format .
```

CI can run:

```bash
ruff check .
ruff format --check .
```

This keeps quality gates visible without adding unnecessary tooling complexity.


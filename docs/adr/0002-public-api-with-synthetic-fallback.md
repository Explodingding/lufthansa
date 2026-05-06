# ADR 0002: Public API With Synthetic Fallback

## Status

Accepted

## Context

The role requires experience with data extraction from APIs. Public APIs can be unreliable for portfolio demos because they may require keys, enforce rate limits, or change response formats.

## Decision

The project will use a public API where practical and keep a synthetic fallback dataset generator.

The public API path demonstrates real extraction concerns:

- HTTP calls,
- response validation,
- contract checks,
- raw landing.

The synthetic fallback guarantees that the project remains runnable during interviews, reviews, and CI.

## Consequences

The project can show API extraction without making the demo fragile. Tests should run only against deterministic local fixtures and synthetic data.
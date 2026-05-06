# Team Context

This project is framed as collaboration between a Middleware team and a Digital Hangar product team.

## Middleware Perspective

The Middleware team owns integration concerns between operational systems and downstream consumers. In this project, that means:

- exposing or forwarding flight, airport, weather, and travel-event data,
- defining stable data contracts,
- handling source-system inconsistencies,
- preserving raw payloads for traceability,
- making integration failures visible,
- enabling reliable downstream processing.

The local implementation represents this through API extractor modules, raw landing files, schema contracts, and tests around input expectations.

## Middleware And Data Engineering Boundary

The boundary between Middleware and Data Engineering is contract-based, not team-name-based.

Middleware usually owns making data available reliably. Data Engineering usually owns making that data trustworthy and useful for analytics. The exact split can be fluid depending on source-system maturity, team setup, and integration platform capabilities.

In this project, the boundary is the agreed data contract. Middleware-style sources provide API-like payloads or files, and the data platform validates those payloads before turning them into analytical datasets.

## Digital Hangar Perspective

Digital Hangar owns digital travel experience outcomes. In this project, that means:

- turning operational data into product insights,
- monitoring disruption and punctuality indicators,
- supporting product owners and business analysts with dashboard metrics,
- enabling data scientists to explore curated datasets,
- improving the passenger-facing digital journey with evidence from data.

The local implementation represents this through gold analytical tables, SQL insights, exploratory notebooks, and a Streamlit dashboard.

## Delivery Team Simulation

The repository is designed as if it were delivered by a small cross-functional team:

- backend developer: extractor and service-style code structure,
- architect: data lake layers, ADRs, cloud blueprint,
- data scientist: exploration notebook and feature-ready datasets,
- product owner and business analyst: acceptance criteria and business metrics,
- scrum master or project manager: MVP scope and incremental delivery,
- data engineer: pipelines, tests, quality rules, SQL, CI/CD.
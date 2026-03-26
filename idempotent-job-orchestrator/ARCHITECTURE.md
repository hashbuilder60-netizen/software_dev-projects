# Architecture Notes

## Design Goals

- Model operational concerns beyond basic CRUD
- Keep the persistence layer deterministic and inspectable for local evaluation
- Make lifecycle transitions auditable
- Expose metrics and request identifiers so runtime behavior is observable

## Core Decisions

- SQLite is used for deterministic local persistence instead of an in-memory store
- `idempotency_key` is persisted and deduplicated at the application boundary
- Jobs carry a `revision` that increments on each state mutation
- Every meaningful state change produces an `audit_event`
- Control-plane routes require `X-API-Key`; `/health` and `/metrics` remain open for platform integrations

## Tradeoffs

- SQLite keeps the project easy to run, but it is not a horizontal scaling story
- API-key auth is simpler than OAuth/JWT and appropriate for service-to-service control-plane access in a portfolio project
- Prometheus metrics are intentionally lightweight; the goal is to demonstrate operational instrumentation, not full telemetry infrastructure

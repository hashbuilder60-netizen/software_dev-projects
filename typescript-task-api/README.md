# TypeScript Task API

A production-leaning Express service in TypeScript that demonstrates idempotent creation, optimistic concurrency, filterable listing, operational stats, and lightweight durable persistence.

## Core Behaviors

- `Idempotency-Key` support on create to suppress duplicate writes
- Optimistic concurrency via `expectedVersion` on updates
- Filterable listing by `status`, `priority`, and free-text query
- File-backed persistence for deterministic local execution
- App factory + test harness with Vitest and Supertest

## API Surface

- `GET /health`
- `GET /v1/work-items`
- `GET /v1/work-items/stats`
- `GET /v1/work-items/:id`
- `POST /v1/work-items`
- `PATCH /v1/work-items/:id`

## Local Run

```powershell
cd typescript-task-api
npm install
npm run dev
```

## Validation

```powershell
cd typescript-task-api
npm run typecheck
npm test
```

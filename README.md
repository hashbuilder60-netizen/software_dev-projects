# Software Dev Projects

A curated monorepo of production-leaning services, platform primitives, and operational reference implementations spanning APIs, orchestration, data, observability, and delivery automation.

## Advanced Highlights

- `fastapi-task-api/` uses layered architecture, SQLite persistence, filtering, pagination, and operational stats
- `idempotent-job-orchestrator/` models idempotent writes, retry scheduling, and explicit job lifecycle transitions
- `typescript-task-api/` now demonstrates idempotency, optimistic concurrency, and contract-style service boundaries
- `repo-health.yml` and `tools/repo_health.py` enforce monorepo hygiene instead of relying on convention alone
- CI workflows are centralized at the repository root so every active pipeline is actually enforced by GitHub Actions
- `docs/monorepo-architecture.md` documents how the portfolio should evolve as projects move toward production-grade standards

## Projects

1. `aws-deploy-pipeline/` - Terraform + GitHub Actions AWS deployment template.
2. `dev-journal-cli/` - SQLite-backed developer workflow CLI with tests and packaging.
3. `fastapi-task-api/` - Layered FastAPI service with persistence, filtering, and richer operational semantics.
4. `frontend-portfolio-showcase/` - Responsive frontend showcase for portfolio-oriented web delivery.
5. `idempotent-job-orchestrator/` - Operational orchestration service with idempotency keys, retry windows, and lifecycle transitions.
6. `jwt-auth-service/` - TypeScript authentication service with JWT-based access control.
7. `node-file-organizer-cli/` - Node.js CLI for filesystem normalization and dry-run execution.
8. `observability-demo/` - FastAPI observability reference app with logs, metrics, and Sentry integration.
9. `postgres-docker-starter/` - Local data platform starter with PostgreSQL and containerized bootstrap scripts.
10. `python-algorithms-toolkit/` - Reference implementations for core algorithmic patterns.
11. `redis-queue-worker/` - Queue producer/worker reference for background processing patterns.
12. `typescript-task-api/` - TypeScript + Express service with optimistic concurrency, idempotency semantics, and operational listing/stats.

## Repository Standards

- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.editorconfig`
- `.gitattributes`
- `.github/CODEOWNERS`
- issue templates + PR template
- Dependabot config
- repo health workflow + structure validator
- centralized root-level CI workflows

## Profile Files

- `PROFILE_README.md`
- `PROFILE_README_TEMPLATE.md`

## Author

Created by [hashbuilder60-netizen](https://github.com/hashbuilder60-netizen)

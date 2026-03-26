# Monorepo Architecture

This repository is organized as a portfolio monorepo, but each folder is expected to feel like a standalone project rather than a loose demo.

## Project Groups

- `backend-services`: `fastapi-task-api`, `jwt-auth-service`, `observability-demo`
- `orchestration-and-workflows`: `idempotent-job-orchestrator`, `redis-queue-worker`
- `cli-and-tooling`: `dev-journal-cli`, `node-file-organizer-cli`, `redis-queue-worker`
- `frontend-and-web`: `frontend-portfolio-showcase`, `web integrations in other repos`
- `platform-and-infra`: `postgres-docker-starter`, `aws-deploy-pipeline`
- `learning-and-algorithms`: `python-algorithms-toolkit`, `CCNA-Networking-Labs` in a separate repo

## Quality Rules

- Every project must have its own `README.md`
- The root `README.md` should mention every top-level project directory
- Generated Python artifacts like `__pycache__` and `.pyc` files should never be committed
- Projects should prefer tests and CI over placeholder-only scaffolds

## Advanced Direction

- Prefer layered application design for APIs
- Prefer persistence-backed examples over in-memory-only demos
- Add observability, CI, and deployment paths when a project grows
- Keep each project teachable: small enough to explain, realistic enough to showcase

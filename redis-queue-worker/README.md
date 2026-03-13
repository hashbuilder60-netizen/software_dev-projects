# Redis Queue Worker

Simple producer/worker demo using Redis lists and blocking pop.

## Run

1. Start Redis (Docker is easiest):
```powershell
docker run --rm -p 6379:6379 redis:7
```
2. In another terminal:
```powershell
cd redis-queue-worker
pip install -e .
queue-worker
```
3. In another terminal:
```powershell
cd redis-queue-worker
queue-producer
```
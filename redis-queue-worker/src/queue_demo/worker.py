import json
import os
import time
from redis import Redis


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue = os.getenv("QUEUE_NAME", "jobs")
    client = Redis.from_url(redis_url, decode_responses=True)

    print("worker started; waiting for jobs...")
    while True:
        item = client.blpop(queue, timeout=5)
        if not item:
            continue
        _, payload = item
        job = json.loads(payload)
        print(f"processing job {job['job_id']} -> {job['action']} for {job['to']}")
        time.sleep(1)
import json
import os
from redis import Redis


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue = os.getenv("QUEUE_NAME", "jobs")
    client = Redis.from_url(redis_url, decode_responses=True)

    for i in range(1, 6):
        payload = {"job_id": i, "action": "send_email", "to": f"user{i}@example.com"}
        client.rpush(queue, json.dumps(payload))
        print(f"queued job {i}")


if __name__ == "__main__":
    main()
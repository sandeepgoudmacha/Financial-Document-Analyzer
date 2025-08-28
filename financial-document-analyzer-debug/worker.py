# worker.py
from redis import Redis
from rq import Queue, Worker
import sys
import os

# Add current directory to Python path so all local modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Redis connection setup
redis_conn = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
)

# Queue setup
queue = Queue(connection=redis_conn)

if __name__ == "__main__":
    print("🚀 Starting RQ worker...")
    print(f"✅ Connected to Redis at {redis_conn}")
    print(f"📌 Listening on queue: {queue.name}")

    # Create worker instance
    worker = Worker([queue], connection=redis_conn)

    print("👷 Worker started. Waiting for jobs...")
    worker.work()

from redis import Redis
from rq import Queue
from tasks import process_financial_report  # <-- your main task

redis_conn = Redis(host="localhost", port=6379, db=0)
queue = Queue(connection=redis_conn)

if __name__ == "__main__":
    job = queue.enqueue(
        process_financial_report,
        "Analyze my financial report",
        "data/financial_report.pdf",
        "financial_hash_123"
    )
    print(f"✅ Job {job.id} enqueued! Status: {job.get_status()}")

# app.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from rq import Queue
import shutil
import os
import uuid

# Import your task
from tasks import process_financial_report

# Init FastAPI
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis + RQ
redis_conn = Redis(host="localhost", port=6379, db=0)
queue = Queue(connection=redis_conn)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze")
async def analyze(query: str = Form(...), file: UploadFile = None):
    # Save uploaded PDF
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Enqueue job
    job = queue.enqueue(process_financial_report, query, file_path, file_id)
    return {"job_id": job.id, "file_id": file_id, "status": "queued"}

@app.get("/result/{job_id}")
def get_result(job_id: str):
    result = redis_conn.hgetall(f"financial_result:{job_id}")
    if not result:
        return {"status": "pending", "message": "Result not ready yet."}

    decoded = {k.decode(): v.decode() for k, v in result.items()}
    return {"status": "done", "result": decoded}
